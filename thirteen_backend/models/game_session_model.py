from enum import StrEnum
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from thirteen_backend.models import Base


class GameStatus(StrEnum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[GameStatus] = mapped_column(String(20), default=GameStatus.CREATED)
    placements: Mapped[list[dict[str, int]] | None] = mapped_column(JSONB, nullable=True)

    # relationships
    game_events: Mapped[list["GameEvent"]] = relationship()
    game_players: Mapped[list["GamePlayer"]] = relationship()