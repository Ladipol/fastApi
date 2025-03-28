"""add foreign-key to post table

Revision ID: 26563695ec02
Revises: dfb27adc5140
Create Date: 2025-03-27 19:35:55.817070

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "26563695ec02"
down_revision: Union[str, None] = "dfb27adc5140"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("post", sa.Column("owner_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "fk_post_owner_id", "post", "users", ["owner_id"], ["id"], ondelete="CASCADE"
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_post_owner_id", "post", type_="foreignkey")
    op.drop_column("post", "owner_id")
    pass
