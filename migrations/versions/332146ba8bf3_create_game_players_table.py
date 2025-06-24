"""create_game_players_table

Revision ID: 332146ba8bf3
Revises: 60a45917c7d2
Create Date: 2025-06-23 16:54:30.597811

"""

from uuid import uuid4
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "332146ba8bf3"
down_revision: Union[str, Sequence[str], None] = "60a45917c7d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "game_players",
        sa.Column("id", sa.UUID, primary_key=True, default=uuid4),
        sa.Column(
            "game_id",
            sa.UUID,
            sa.ForeignKey("game_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "player_id",
            sa.UUID,
            sa.ForeignKey("players.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("seat_number", sa.Integer, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("game_players")
