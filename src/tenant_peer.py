import ipaddress
import typing

import fastapi

from entities import ClientJoinRequest, ClientJoinResponse, PeerInfo, PeerRemovalMessage
from logger import get_logger


class TenantPeer:
    def __init__(self, websocket: fastapi.WebSocket, virtual_ip: ipaddress.IPv4Address):
        self._display_name = None
        self._public_key = None
        self._virtual_ip = virtual_ip
        self._websocket = websocket
        self._logger = get_logger()

    async def complete_handshake(self, tenant_peers: typing.List[PeerInfo]):
        await self._receive_join_request()
        await self._send_join_response(tenant_peers)

    async def _receive_join_request(self):
        self._logger.info(f"Awaiting peer information from new client `{self._websocket.client.host}`")
        raw_join_request = await self._websocket.receive_text()
        join_request = ClientJoinRequest.parse_raw(raw_join_request)
        self._display_name = join_request.display_name
        self._public_key = join_request.public_key

    async def _send_join_response(self, tenant_peers: typing.List[PeerInfo]):
        self._logger.info(f"Sending new client `{self._websocket.client.host}` its joining response")
        join_response = ClientJoinResponse(virtual_ip=self._virtual_ip, peers=tenant_peers)
        await self._websocket.send_text(join_response.json())

    async def push_notification(self, notification: PeerInfo | PeerRemovalMessage, raise_error=True):
        try:
            await self._websocket.send_text(notification.json())
        except Exception:
            if raise_error:
                raise
            else:
                self._logger.exception(f"Error while trying to push notification to `{self._virtual_ip}`")

    def get_info(self) -> PeerInfo:
        return PeerInfo(
            display_name=self._display_name,
            public_key=self._public_key,
            virtual_ip=self._virtual_ip
        )
