from datetime import datetime
from enum import StrEnum
from typing import Any, Literal, TypedDict

from pydantic import BaseModel

from thirteen_backend.domain.card import Card


class GameConfig(BaseModel):
    times_shuffled: int
    deck_count: int
    players_count: int


WebSocketMessageType = Literal["PLAY", "PASS", "READY", "PING", "RESYNC"]


class WebSocketMessage(BaseModel):
    type: WebSocketMessageType
    session_id: str
    player_id: str
    last_sequence: int
    timestamp: datetime
    payload: list[dict[str, Any]] | None


class PlayType(StrEnum):
    OPEN = "open"
    SINGLE = "single"
    PAIR = "pair"
    TRIPLET = "triplet"
    SEQUENCE = "sequence"
    DOUBLE_SEQUENCE = "double_sequence"
    QUARTET = "quartet"


class Play(TypedDict):
    cards: list[Card]
    play_type: PlayType
