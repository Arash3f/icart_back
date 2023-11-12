"""empty message

Revision ID: e2da994dffb9
Revises: c2211faca656
Create Date: 2023-11-11 11:46:32.592971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e2da994dffb9"
down_revision: Union[str, None] = "c2211faca656"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TYPE logtype ADD VALUE 'UPDATE_MERCHANT'")
    op.execute("ALTER TYPE logtype ADD VALUE 'ADD_POS'")
    op.execute("ALTER TYPE logtype ADD VALUE 'DELETE_POS'")
    op.execute("ALTER TYPE logtype ADD VALUE 'UPDATE_POS'")
    op.execute("ALTER TYPE logtype ADD VALUE 'UPDATE_USER'")
    op.execute("ALTER TYPE logtype ADD VALUE 'UPDATE_USER_ACTIVITY'")
    op.execute("ALTER TYPE logtype ADD VALUE 'GENERATE_ORGANIZATION_USER'")
    op.execute("ALTER TYPE logtype ADD VALUE 'APPEND_ORGANIZATION_USER'")
    op.execute("ALTER TYPE logtype ADD VALUE 'ACTIVE_ORGANIZATION_USER'")
    op.execute("ALTER TYPE logtype ADD VALUE 'UPDATE_POSITION_REQUEST'")
    op.execute("ALTER TYPE logtype ADD VALUE 'CREATE_POSITION_REQUEST'")
    op.execute("ALTER TYPE logtype ADD VALUE 'APPROVE_POSITION_REQUEST'")
    op.add_column("card", sa.Column("forget_password", sa.String(), nullable=True))
    op.add_column(
        "card",
        sa.Column("forget_password_exp", sa.DateTime(timezone=True), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("card", "forget_password_exp")
    op.drop_column("card", "forget_password")
    # ### end Alembic commands ###
