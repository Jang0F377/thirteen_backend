from uuid import UUID, uuid4
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from thirteen_backend.models import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_bot: Mapped[bool] = mapped_column(nullable=False)

    # relationships
    game_players: Mapped[list["GamePlayer"]] = relationship()
