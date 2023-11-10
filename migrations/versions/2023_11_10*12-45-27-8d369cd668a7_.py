"""empty message

Revision ID: 8d369cd668a7
Revises: 9045f2ce819e
Create Date: 2023-11-10 12:45:27.976540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8d369cd668a7"
down_revision: Union[str, None] = "9045f2ce819e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user_request", sa.Column("status", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user_request", "status")
    # ### end Alembic commands ###