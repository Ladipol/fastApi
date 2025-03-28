"""add content column to post table

Revision ID: c7843ceaf700
Revises: 3b2e1ccba0b9
Create Date: 2025-03-27 18:55:39.248242

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7843ceaf700"
down_revision: Union[str, None] = "3b2e1ccba0b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("post", sa.Column("content", sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("post", "content")
    pass
