import ipaddress
import typing

import pydantic


class PeerInfo(pydantic.BaseModel):
    display_name: typing.Optional[str]  # Could be None if the peer handshake process wasn't complete
    public_key: typing.Optional[bytes]  # Could be None if the peer handshake process wasn't complete
    virtual_ip: ipaddress.IPv4Address


class ClientJoinRequest(pydantic.BaseModel):
    display_name: str
    public_key: bytes


class ClientJoinResponse(pydantic.BaseModel):
    virtual_ip: ipaddress.IPv4Address
    peers: typing.List[PeerInfo]


class PeerRemovalMessage(pydantic.BaseModel):
    removed_peer: ipaddress.IPv4Address
