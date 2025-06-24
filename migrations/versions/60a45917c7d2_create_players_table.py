"""create_players_table

Revision ID: 60a45917c7d2
Revises: f5d9494657ad
Create Date: 2025-06-23 16:53:41.727950

"""
from uuid import uuid4
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60a45917c7d2'
down_revision: Union[str, Sequence[str], None] = 'f5d9494657ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'players',
        sa.Column('id', sa.UUID, primary_key=True, default=uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_bot', sa.Boolean, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('players')
