"""add phone-number

Revision ID: 877410e46a57
Revises: feb14187f2f7
Create Date: 2025-03-27 20:29:47.945920

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlmodel import AutoString


# revision identifiers, used by Alembic.
revision: str = "877410e46a57"
down_revision: Union[str, None] = "feb14187f2f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column("phone_num", AutoString(), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "phone_num")
    # ### end Alembic commands ###
