import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status

from logger import get_logger, initialize_logger
from tenant_creator import TenantCreator

app = FastAPI()
tenant_pool = TenantCreator()


@app.websocket("/tenants/{tenant_id}")
async def client_endpoint(websocket: WebSocket, tenant_id: str):
    logger = get_logger()
    logger.info(f"Received a new connection from {websocket.client.host}, asking to join tenant {tenant_id}")

    await websocket.accept()
    tenant = None

    try:
        tenant = tenant_pool.get(tenant_id)
        await tenant.add_peer(websocket)

        # Client should not send any more messages to the server, and only receive push notifications.
        # This will block until the client disconnection that would raise `WebSocketDisconnect` exception.
        await websocket.receive_text()

    except WebSocketDisconnect:
        logger.info(f"Connection from {websocket.client.host} was closed")

    except Exception:
        logger.exception("Error occurred while handling client, closing connection.")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

    finally:
        if tenant is not None:
            await tenant.remove_peer(websocket)

            # TODO: Maybe lock?
            if tenant.get_active_peers_number() == 0:
                tenant_pool.remove(tenant_id)


@app.on_event("startup")
async def initialize_server():
    """
    This function runs on server startup and initializes the logger.
    """
    initialize_logger()


if __name__ == '__main__':
    uvicorn.run(app)
