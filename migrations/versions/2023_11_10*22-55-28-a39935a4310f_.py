"""empty message

Revision ID: a39935a4310f
Revises: 8d369cd668a7
Create Date: 2023-11-10 22:55:28.670958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from src.log.models import LogType

# revision identifiers, used by Alembic.
revision: str = "a39935a4310f"
down_revision: Union[str, None] = "8d369cd668a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    log_type = postgresql.ENUM(
        LogType,
        name="logtype",
    )
    log_type.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "log",
        sa.Column("type", log_type, nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("log", "type")
    # ### end Alembic commands ###
