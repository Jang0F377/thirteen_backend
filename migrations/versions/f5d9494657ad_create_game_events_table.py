"""create_game_events_table

Revision ID: f5d9494657ad
Revises: 6ec4b10928bb
Create Date: 2025-06-23 16:49:33.836122

"""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f5d9494657ad"
down_revision: Union[str, Sequence[str], None] = "6ec4b10928bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "game_events",
        sa.Column("id", sa.UUID, primary_key=True, default=uuid4),
        sa.Column("seq", sa.Integer, nullable=False),
        sa.Column("turn", sa.Integer, nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("payload", sa.JSON, nullable=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "game_id",
            sa.UUID,
            sa.ForeignKey("game_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("game_events")
