from types import SimpleNamespace

import pytest

from thirteen_backend.services.websocket.websocket_manager import WebSocketManager


class DummyWebSocket:
    """A lightweight stand-in for FastAPI's WebSocket used in unit tests."""

    def __init__(self, host: str = "test", port: int = 12345):
        # FastAPI's WebSocket exposes a `client` attribute with host/port
        self.client = SimpleNamespace(host=host, port=port)
        self.accepted = False
        self.sent: list[tuple[str, object]] = []

    async def accept(self):
        self.accepted = True

    async def send_text(self, text: str):
        self.sent.append(("text", text))

    async def send_json(self, data):
        self.sent.append(("json", data))


@pytest.mark.asyncio
async def test_connect_broadcast_send_disconnect():
    manager = WebSocketManager()

    ws = DummyWebSocket()

    # Connect
    conn_id = await manager.connect("session123", ws)
    assert manager.session_count() == 1
    assert manager.connection_count("session123") == 1
    assert ws.accepted is True

    # Broadcast JSON message
    message = {"hello": "world"}
    await manager.broadcast("session123", message)
    assert ("json", message) in ws.sent

    # Send string specifically to the connection
    delivered = await manager.send_to("session123", conn_id, "ping")
    assert delivered is True
    assert ("text", "ping") in ws.sent

    # Disconnect and ensure bookkeeping is cleaned
    manager.disconnect("session123", ws)
    assert manager.connection_count("session123") == 0
