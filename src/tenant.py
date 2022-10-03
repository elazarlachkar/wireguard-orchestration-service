import asyncio
import typing

import fastapi

from entities import PeerInfo, PeerRemovalMessage
from exceptions import PeerJoinError, PeerRemovalError
from logger import get_logger
from overlay_network import OverlayNetwork
from tenant_peer import TenantPeer


class Tenant:
    """
    A tenant contains multiple peers that can communicate with each other.

    Each peer has a public key and a virtual IP address that belongs to the tenant's network. Using those 2 items,
    other peers can communicate with it.
    """
    def __init__(self, overlay_network: OverlayNetwork):
        """
        :param overlay_network: The tenant's overlay network, used to allocate virtual IP addresses to the peers.
        """
        self._peers: typing.Dict[fastapi.WebSocket, TenantPeer] = {}
        self._overlay_network = overlay_network
        self._logger = get_logger()

    async def add_peer(self, websocket: fastapi.WebSocket):
        """
        Adds a peer to the tenant.
        After a virtual IP address is allocated to the new peer in the tenant's network, the joining handshake is
        completed and a broadcast message is sent to all existing peers notifying them of the new peer.

        :param websocket: The WebSocket connection to the peer.

        :raises PeerJoinError: In case an error occurred while adding the peer.
        """
        try:
            current_tenant_peers_info = [peer.get_info() for peer in self._peers.values()]

            new_peer_ip_address = self._overlay_network.allocate_ip_address()
            self._logger.info(f"Allocated virtual IP `{new_peer_ip_address}` to new client `{websocket.client.host}`")

            try:
                new_peer = TenantPeer(websocket, new_peer_ip_address)
                await new_peer.complete_handshake(current_tenant_peers_info)
            except Exception:
                self._overlay_network.free_ip_address(new_peer_ip_address)
                raise

            new_peer_info = new_peer.get_info()

            self._logger.info(f"Sending tenant a peer join notification")
            await self._broadcast_notification(new_peer_info)

        except Exception as error:
            raise PeerJoinError() from error

        self._peers[websocket] = new_peer
        self._logger.info(f"New peer join successfully the tenant! Peer Info: {new_peer_info}")

    async def remove_peer(self, websocket: fastapi.WebSocket):
        """
        Removes a peer from the tenant.
        The peer's virtual IP address is freed (to be used by future peers in the tenant), and then a broadcast message
        is sent to all the tenant's peers notifying them of the peer's removal.

        :param websocket: The WebSocket connection to the peer.

        :raises PeerRemovalError: In case an error occurred while removing the peer.
        """
        self._logger.info(f"Removing client {websocket.client.host} from tenant")
        try:
            removed_peer = self._peers.pop(websocket)
            removed_peer_ip = removed_peer.get_info().virtual_ip

            self._logger.info(f"Sending tenant a peer removal notification")
            peer_removal_notification = PeerRemovalMessage(removed_peer=removed_peer_ip)
            await self._broadcast_notification(peer_removal_notification)

            self._overlay_network.free_ip_address(removed_peer_ip)
            self._logger.info(f"Freed virtual IP {removed_peer_ip} to future use")

        except Exception as error:
            raise PeerRemovalError() from error

    async def _broadcast_notification(self, notification: PeerInfo | PeerRemovalMessage):
        """
        Broadcasts a notification to all existing peers in the tenant.
        """
        coroutines = [peer.push_notification(notification, raise_error=False) for peer in self._peers.values()]
        await asyncio.gather(*coroutines)

    def get_active_peers_number(self) -> int:
        return len(self._peers.keys())

    def get_overlay_network(self) -> OverlayNetwork:
        return self._overlay_network
