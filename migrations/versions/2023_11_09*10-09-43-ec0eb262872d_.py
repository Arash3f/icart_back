"""empty message

Revision ID: ec0eb262872d
Revises: 6e19d3832fd0
Create Date: 2023-11-09 10:09:43.193960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from src.transaction.models import TransactionStatusEnum

# revision identifiers, used by Alembic.
revision: str = "ec0eb262872d"
down_revision: Union[str, None] = "6e19d3832fd0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    transaction_status_enum = postgresql.ENUM(
        TransactionStatusEnum,
        name="transactionstatusenum",
    )
    transaction_status_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "transaction",
        sa.Column("status", transaction_status_enum, nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("transaction", "status")
    # ### end Alembic commands ###