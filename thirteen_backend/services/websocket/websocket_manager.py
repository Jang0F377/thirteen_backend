"""Utility class that manages WebSocket connections per session.

Abstracts connection bookkeeping away from the FastAPI endpoint so the rest
of the backend can simply call `websocket_manager.broadcast(session_id, msg)`.
"""

import logging
import uuid
from typing import Any, Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

# Metrics
from thirteen_backend import metrics

logger = logging.getLogger("websocket-manager")


class WebSocketManager:  # pylint: disable=too-few-public-methods
    """Keeps track of active sockets per session and provides broadcast."""

    def __init__(self) -> None:
        self._active: Dict[str, Dict[str, WebSocket]] = {}

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------
    async def connect(self, session_id: str, ws: WebSocket) -> str:
        """Accept the WebSocket and register it under *session_id*."""
        await ws.accept()
        conn_id = self._connection_key(ws)
        self._active.setdefault(session_id, {})[conn_id] = ws
        # Metrics: increment active connections gauge
        metrics.increment_ws_connections(session_id=session_id)
        logger.info("WS connected: session=%s conn=%s", session_id, conn_id)
        return conn_id

    def disconnect(self, session_id: str, ws: WebSocket) -> None:
        """Remove the socket from bookkeeping (does *not* close it)."""
        conn_id = self._connection_key(ws)
        if session_id in self._active and conn_id in self._active[session_id]:
            self._active[session_id].pop(conn_id, None)
            if not self._active[session_id]:
                del self._active[session_id]
        # Metrics: decrement active connections gauge
        metrics.decrement_ws_connections(session_id=session_id)
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
                # Metrics: count successfully delivered websocket messages
                metrics.increment_ws_messages(
                    session_id=session_id, direction="broadcast"
                )
            except WebSocketDisconnect:
                dead.add(conn_id)
        for conn_id in dead:
            self._active[session_id].pop(conn_id, None)
        if dead:
            logger.info(
                "Cleaned %d dead sockets from session %s", len(dead), session_id
            )

    async def send_to(
        self,
        session_id: str,
        conn_id: str,
        message: Any,
    ) -> bool:
        """Send *message* to one connection. Returns True if delivered."""
        ws = self._active.get(session_id, {}).get(conn_id)
        if ws is None:  # not found / already gone
            return False
        try:
            if isinstance(message, str):
                await ws.send_text(message)
            else:
                await ws.send_json(message)
            # Metrics: count successfully delivered websocket messages (direct)
            metrics.increment_ws_messages(session_id=session_id, direction="direct")
            return True
        except WebSocketDisconnect:
            # cleanup & report failure
            self.disconnect(session_id, ws)
            return False

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
