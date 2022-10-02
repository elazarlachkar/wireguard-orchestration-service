import ipaddress
import typing

import fastapi

from entities import ClientJoinRequest, ClientJoinResponse, PeerInfo, PeerRemovalMessage
from logger import get_logger


class TenantPeer:
    """
    This class represents a peer that is a part of a tenant.
    """
    def __init__(self, websocket: fastapi.WebSocket, virtual_ip: ipaddress.IPv4Address):
        """
        :param websocket: The WebSocket connection to the peer.
        :param virtual_ip: The peer IP address in the tenant overlay network.
        """
        self._display_name = None
        self._public_key = None
        self._virtual_ip = virtual_ip
        self._websocket = websocket
        self._logger = get_logger()

    async def complete_handshake(self, tenant_peers: typing.List[PeerInfo]):
        """
        Each new peer has to complete a handshake in order to join the tenant. This method executed the handshake.
        The handshake consists of two steps:
            1. The new peer send its join request, that includes its display name and public key.
            2. The server send the new peer a response, that includes its virtual ip address in the tenant's network
                and information about the other peers in the tenant.
        """
        await self._receive_join_request()
        await self._send_join_response(tenant_peers)

    async def _receive_join_request(self):
        """
        Receives a new peer join request, which includes its display name and public key in a JSON format.
        """
        self._logger.info(f"Awaiting peer information from new client `{self._websocket.client.host}`")
        raw_join_request = await self._websocket.receive_text()
        join_request = ClientJoinRequest.parse_raw(raw_join_request)
        self._display_name = join_request.display_name
        self._public_key = join_request.public_key

    async def _send_join_response(self, tenant_peers: typing.List[PeerInfo]):
        """
        Sends a new peer a join response, which includes its virtual ip address in the tenant's network and information
        about the other peers in the tenant.
        """
        self._logger.info(f"Sending new client `{self._websocket.client.host}` its joining response")
        join_response = ClientJoinResponse(virtual_ip=self._virtual_ip, peers=tenant_peers)
        await self._websocket.send_text(join_response.json())

    async def push_notification(self, notification: PeerInfo | PeerRemovalMessage, raise_error=True):
        """
        Push a new notification to the peer.
        If the `raise_error` flag is Ture, an exception is raised in case of an error. Otherwise, the error is only
        logged.
        """
        try:
            await self._websocket.send_text(notification.json())
        except Exception:
            if raise_error:
                raise
            else:
                self._logger.exception(f"Error while trying to push notification to `{self._virtual_ip}`")

    def get_info(self) -> PeerInfo:
        """
        Returns the peer information.
        """
        return PeerInfo(
            display_name=self._display_name,
            public_key=self._public_key,
            virtual_ip=self._virtual_ip
        )
