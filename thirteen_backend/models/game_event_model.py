from enum import StrEnum
from typing import Any
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4
from datetime import datetime, timezone
from thirteen_backend.models import Base


class GameEventType(StrEnum):
    PLAY = "PLAY"
    PASS = "PASS"
    JOIN = "JOIN"
    LEAVE = "LEAVE"
    START = "START"
    END = "END"


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
