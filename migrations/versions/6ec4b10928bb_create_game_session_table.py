"""create_game_session_table

Revision ID: 6ec4b10928bb
Revises:
Create Date: 2025-06-23 16:45:31.201974

"""

from uuid import uuid4
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6ec4b10928bb"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "game_sessions",
        sa.Column("id", sa.UUID, primary_key=True, default=uuid4),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="created"),
        sa.Column("placements", sa.JSON, nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("game_sessions")
