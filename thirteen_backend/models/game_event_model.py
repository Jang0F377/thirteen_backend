from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from thirteen_backend.models import Base
from thirteen_backend.utils.format_utils import format_datetime, format_uuid_as_str


class GameEventType(StrEnum):
    PLAY = "PLAY"
    PASS = "PASS"
    JOIN = "JOIN"
    LEAVE = "LEAVE"
    START = "START"
    FINISH = "FINISH"
    INIT = "INIT"
    STATE_SYNC = "STATE_SYNC"


class GameEvent(Base):
    __tablename__ = "game_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    turn: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[GameEventType] = mapped_column(String(20), nullable=False)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # relationships
    game_id: Mapped[UUID] = mapped_column(ForeignKey("game_sessions.id"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": format_uuid_as_str(self.id),
            "seq": self.seq,
            "turn": self.turn,
            "type": self.type,
            "payload": self.payload,
            "ts": format_datetime(self.ts),
            "game_id": format_uuid_as_str(self.game_id),
        }
