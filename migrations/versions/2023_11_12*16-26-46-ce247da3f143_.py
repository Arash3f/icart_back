"""empty message

Revision ID: ce247da3f143
Revises: 378bbf23cf32
Create Date: 2023-11-12 16:26:46.323968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ce247da3f143"
down_revision: Union[str, None] = "378bbf23cf32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TYPE logtype ADD VALUE 'BUY_CARD'")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
