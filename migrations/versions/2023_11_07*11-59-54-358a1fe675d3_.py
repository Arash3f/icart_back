"""empty message

Revision ID: 358a1fe675d3
Revises: e2bbedecb006
Create Date: 2023-11-07 11:59:54.772620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "358a1fe675d3"
down_revision: Union[str, None] = "e2bbedecb006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TYPE sellingtype ADD VALUE 'AUDIO_AND_VIDEO_PRODUCT_STORE'")
    op.execute(
        "ALTER TYPE sellingtype ADD VALUE 'KITCHEN_ACCESSORIES_STORE'",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###