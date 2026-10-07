"""add subdirectory column to projects

Revision ID: c2a7e5f91b3d
Revises: fa2593a3dc07
Create Date: 2026-08-30 10:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c2a7e5f91b3d'
down_revision: str | None = 'fa2593a3dc07'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('projects', sa.Column('subdirectory', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('projects', 'subdirectory')
