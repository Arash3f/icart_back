"""empty message

Revision ID: c3607e714eaf
Revises: b9bab83d2b69
Create Date: 2023-10-29 15:07:49.064565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3607e714eaf"
down_revision: Union[str, None] = "b9bab83d2b69"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("credit", sa.Column("active", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("credit", "active")
    # ### end Alembic commands ###
