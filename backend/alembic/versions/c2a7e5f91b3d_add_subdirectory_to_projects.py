"""add subdirectory column to projects

Revision ID: c2a7e5f91b3d
Revises: fa2593a3dc07
Create Date: 2026-08-30 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2a7e5f91b3d'
down_revision: Union[str, None] = 'fa2593a3dc07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('projects', sa.Column('subdirectory', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('projects', 'subdirectory')
