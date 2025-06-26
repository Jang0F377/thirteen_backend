"""Utility class that manages WebSocket connections per session.

Abstracts connection bookkeeping away from the FastAPI endpoint so the rest
of the backend can simply call `websocket_manager.broadcast(session_id, msg)`.
"""

import uuid
import logging
from typing import Dict, Any, Set

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("websocket-manager")


class WebSocketManager:  # pylint: disable=too-few-public-methods
    """Keeps track of active sockets per session and provides broadcast."""

    def __init__(self) -> None:
        self._active: Dict[str, Dict[str, WebSocket]] = {}

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------
    async def connect(self, session_id: str, ws: WebSocket) -> None:
        """Accept the WebSocket and register it under *session_id*."""
        await ws.accept()
        conn_id = self._connection_key(ws)
        self._active.setdefault(session_id, {})[conn_id] = ws
        logger.info("WS connected: session=%s conn=%s", session_id, conn_id)
        return ws

    def disconnect(self, session_id: str, ws: WebSocket) -> None:
        """Remove the socket from bookkeeping (does *not* close it)."""
        conn_id = self._connection_key(ws)
        if session_id in self._active and conn_id in self._active[session_id]:
            self._active[session_id].pop(conn_id, None)
            if not self._active[session_id]:
                del self._active[session_id]
        logger.info("WS disconnected: session=%s conn=%s", session_id, conn_id)

    # ------------------------------------------------------------------
    # Broadcast helpers
    # ------------------------------------------------------------------
    async def broadcast(self, session_id: str, message: Any) -> None:
        """Broadcast JSON-serialisable *message* to all sockets in a session."""
        if session_id not in self._active:
            return
        dead: Set[str] = set()
        for conn_id, ws in self._active[session_id].items():
            try:
                # Maintain flexibility: accept both pre-serialised str and dict
                if isinstance(message, str):
                    await ws.send_text(message)
                else:
                    await ws.send_json(message)
            except WebSocketDisconnect:
                dead.add(conn_id)
        for conn_id in dead:
            self._active[session_id].pop(conn_id, None)
        if dead:
            logger.info(
                "Cleaned %d dead sockets from session %s", len(dead), session_id
            )

    # ------------------------------------------------------------------
    # Introspection utilities
    # ------------------------------------------------------------------
    def session_count(self) -> int:
        return len(self._active)

    def connection_count(self, session_id: str) -> int:
        return len(self._active.get(session_id, {}))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _connection_key(ws: WebSocket) -> str:
        if ws.client:
            return f"{ws.client.host}:{ws.client.port}"
        return str(uuid.uuid4())


# Singleton instance – importable everywhere
websocket_manager = WebSocketManager()
