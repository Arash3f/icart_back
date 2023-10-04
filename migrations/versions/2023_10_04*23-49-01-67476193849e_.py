"""empty message

Revision ID: 67476193849e
Revises: 4e62f0574fcf
Create Date: 2023-10-04 23:49:01.304131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "67476193849e"
down_revision: Union[str, None] = "4e62f0574fcf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("transaction", sa.Column("intermediary_id", sa.UUID(), nullable=True))
    op.create_foreign_key(None, "transaction", "wallet", ["intermediary_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "transaction", type_="foreignkey")
    op.drop_column("transaction", "intermediary_id")
    # ### end Alembic commands ###
