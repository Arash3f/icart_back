"""empty message

Revision ID: be6775000d50
Revises: 3fe10f88bdab
Create Date: 2023-11-19 23:29:14.892636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "be6775000d50"
down_revision: Union[str, None] = "3fe10f88bdab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("cash", sa.Column("used", sa.BigInteger(), nullable=True))
    op.add_column("credit", sa.Column("used", sa.BigInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("credit", "used")
    op.drop_column("cash", "used")
    # ### end Alembic commands ###
