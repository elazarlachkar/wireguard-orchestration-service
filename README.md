# Wireguard Orchestration Service

This repository contains the orchestration service for Wireguard VPN. <br/>


### Service API

The service is built on top of the [WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455). <br/>
Each peer maintains a persistent connection to the orchestration service throughout its connection to the VPN. <br/>
Each tenant is identified by a unique ID.

#### Peer Onboarding
On connection, the peer chooses what tenant to join by appending the tenant ID to the URI. If the requested tenant 
doesn't exist, it's created for him. 

> For example, to join tenant `3daf1997-d6eb-41ba-898f-ebc275da1f98`, the client will connect to 
> `ws://{server}:{port}/tenants/3daf1997-d6eb-41ba-898f-ebc275da1f98`.

After a successful connection, the peer is expected to send its 32-byte public key and its display name in the
following JSON format:
```json
{
  "display_name": "{CLIENT'S DISPLAY NAME}",
  "public_key": "{PUBLIC_KEY}"
}
```

> **Warning** <br/>
> Two peers may have the same display name. The identifier of a peer is its private IP address.

At this point, the server will do the following:
- Allocate a virtual IP address that belongs to the tenant's network.
- Return to the client a message containing its allocated IP address and a list of the tenant's peers.
- Broadcast to all tenant's peers that a new peer has joined, with its display name, public key and virtual IP.

The message announcing a peer join should be in the following JSON format:
```json
{
  "display_name": "{CLIENT'S DISPLAY NAME}",
  "public_key": "{PUBLIC_KEY}",
  "virtual_ip": "{IP_ADDRESS}"
}
```

The message returned to the client should be in the following JSON format:
```json
{
  "virtual_ip": "{IP_ADDRESS}",
  "peers": [
    {
      "display_name": "PeerA",
      "public_key": "PeerA-PublicKey",
      "virtual_ip": "PeerA-VirtualIP"
    },
    {
      "display_name": "PeerB",
      "public_key": "PeerB-PublicKey",
      "virtual_ip": "PeerB-VirtualIP"
    }
  ]
}
```

#### Peer Offoarding

If the persistent connection between the client and server is closed from any reason, the client is removed from
the tenant. <br/>
When a client is removed, the server broadcasts a message to all tenant's peers announcing the offboarding, and the
client virtual IP address is freed to be used by others.

The message announcing the client's removal should be in the following JSON format:
```json
{
  "removed_peer": "{CLIENT'S PRIVATE IP ADDRESS}"
}
```