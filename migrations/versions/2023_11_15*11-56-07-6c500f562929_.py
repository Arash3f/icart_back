"""empty message

Revision ID: 6c500f562929
Revises: 4d50c2721c4f
Create Date: 2023-11-15 11:56:07.732835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6c500f562929"
down_revision: Union[str, None] = "4d50c2721c4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        "ALTER TYPE sellingtype RENAME VALUE 'ALL_THREE' TO 'CASH_CREDIT_INSTALLMENT'",
    )
    op.execute("ALTER TYPE sellingtype ADD VALUE 'CASH_CREDIT'")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###