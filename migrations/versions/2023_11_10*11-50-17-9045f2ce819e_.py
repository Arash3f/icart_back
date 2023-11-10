"""empty message

Revision ID: 9045f2ce819e
Revises: 932d6552d692
Create Date: 2023-11-10 11:50:17.059285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9045f2ce819e"
down_revision: Union[str, None] = "932d6552d692"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("merchant", sa.Column("blue_profit", sa.Integer(), nullable=True))
    op.add_column("merchant", sa.Column("silver_profit", sa.Integer(), nullable=True))
    op.add_column("merchant", sa.Column("gold_profit", sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("merchant", "gold_profit")
    op.drop_column("merchant", "silver_profit")
    op.drop_column("merchant", "blue_profit")
    # ### end Alembic commands ###