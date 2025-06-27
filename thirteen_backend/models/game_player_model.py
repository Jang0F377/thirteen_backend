from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from thirteen_backend.models import Base


class GamePlayer(Base):
    __tablename__ = "game_players"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("game_sessions.id"))
    player_id: Mapped[UUID] = mapped_column(ForeignKey("players.id"))
    seat_number: Mapped[int] = mapped_column(nullable=False)
