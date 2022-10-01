import asyncio
import typing

import fastapi

from entities import PeerInfo, PeerRemovalMessage, ClientJoinResponse, ClientJoinRequest
from logger import get_logger
from overlay_network import OverlayNetwork


class Tenant:
    def __init__(self, overlay_network: OverlayNetwork):
        self._peers: typing.Dict[fastapi.WebSocket, PeerInfo] = {}
        self._overlay_network = overlay_network
        self._logger = get_logger()

    async def add_peer(self, websocket: fastapi.WebSocket):
        new_peer = await self._retrieve_new_peer_info(websocket)

        new_peer_join_response = ClientJoinResponse(virtual_ip=new_peer.virtual_ip, peers=list(self._peers.values()))
        self._logger.info(f"Sending new client `{websocket.client.host}` its joining response")
        await websocket.send_text(new_peer_join_response.json())

        await self._broadcast_new_peer_notification(new_peer)
        self._peers[websocket] = new_peer

    async def _broadcast_new_peer_notification(self, new_peer: PeerInfo):
        self._logger.info(f"Sending tenant a peer join notification")
        new_peer_broadcast_message = new_peer.json()
        await self._broadcast(new_peer_broadcast_message)

    async def _retrieve_new_peer_info(self, websocket: fastapi.WebSocket) -> PeerInfo:
        self._logger.info(f"Awaiting peer information from new client `{websocket.client.host}`")
        new_peer_join_raw_request = await websocket.receive_text()
        new_peer_join_request = ClientJoinRequest.parse_raw(new_peer_join_raw_request)

        allocated_ip_address = self._overlay_network.allocate_ip_address()
        self._logger.info(f"Allocated virtual IP `{allocated_ip_address}` to new client `{websocket.client.host}`")

        return PeerInfo(
            display_name=new_peer_join_request.display_name,
            public_key=new_peer_join_request.public_key,
            virtual_ip=allocated_ip_address,
        )

    async def remove_peer(self, websocket: fastapi.WebSocket):
        self._logger.info(f"Removing client {websocket.client.host} from tenant")
        removed_peer = self._peers.pop(websocket)

        await self._broadcast_peer_removal_notification(removed_peer)

        self._overlay_network.free_ip_address(removed_peer.virtual_ip)
        self._logger.info(f"Freed virtual IP {removed_peer.virtual_ip} to future use")

    async def _broadcast_peer_removal_notification(self, peer: PeerInfo):
        self._logger.info(f"Sending tenant a peer removal notification")
        peer_removal_message = PeerRemovalMessage(removed_peer=peer.virtual_ip)
        await self._broadcast(peer_removal_message.json())

    async def _broadcast(self, message: str):
        peers_websockets = list(self._peers.keys())
        coroutines = [websocket.send_text(message) for websocket in peers_websockets]

        self._logger.info(f"Sending message to {len(peers_websockets)} clients")
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        for index in range(len(results)):
            result = results[index]
            websocket = peers_websockets[index]
            if isinstance(result, Exception):
                # TODO: Add a client ID of some sort
                self._logger.warning(f"Error occurred while trying to send message to client: {websocket.client.host}")

    def get_active_peers_number(self) -> int:
        return len(self._peers.keys())

    def get_overlay_network(self) -> OverlayNetwork:
        return self._overlay_network
