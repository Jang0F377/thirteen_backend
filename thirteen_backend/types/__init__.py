from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class GameConfig(BaseModel):
    times_shuffled: int
    deck_count: int
    players_count: int


WebSocketMessageType = Literal["PLAY", "PASS", "READY", "PING", "RESYNC_REQUEST"]


class WebSocketMessage(BaseModel):
    type: WebSocketMessageType
    session_id: str
    player_id: str
    last_sequence: int
    timestamp: datetime
    payload: list[dict[str, Any]] | None
