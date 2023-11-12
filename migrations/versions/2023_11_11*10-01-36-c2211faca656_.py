"""empty message

Revision ID: c2211faca656
Revises: 88d451d6aaa9
Create Date: 2023-11-11 10:01:36.737770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2211faca656"
down_revision: Union[str, None] = "88d451d6aaa9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TYPE logtype ADD VALUE 'ADD_TICKET'")
    op.execute("ALTER TYPE logtype ADD VALUE 'UPDATE_TICKET'")
    op.execute("ALTER TYPE logtype ADD VALUE 'ADD_NEWS'")
    op.execute("ALTER TYPE logtype ADD VALUE 'DELETE_NEWS'")
    op.execute("ALTER TYPE logtype ADD VALUE 'UPDATE_NEWS'")
    op.execute("ALTER TYPE logtype ADD VALUE 'ASSIGN_PERMISSION_TO_ROLE'")
    op.add_column(
        "merchant",
        sa.Column("corporate_profit", sa.Integer(), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("merchant", "corporate_profit")
    # ### end Alembic commands ###