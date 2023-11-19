"""empty message

Revision ID: d949a95a84af
Revises: cdcbed639033
Create Date: 2023-11-19 10:53:11.916888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d949a95a84af"
down_revision: Union[str, None] = "cdcbed639033"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "transaction_intermediary_id_fkey",
        "transaction",
        type_="foreignkey",
    )
    op.drop_constraint(
        "transaction_transferor_id_fkey",
        "transaction",
        type_="foreignkey",
    )
    op.drop_constraint(
        "transaction_receiver_id_fkey",
        "transaction",
        type_="foreignkey",
    )
    op.create_foreign_key(None, "transaction", "card", ["receiver_id"], ["id"])
    op.create_foreign_key(None, "transaction", "card", ["intermediary_id"], ["id"])
    op.create_foreign_key(None, "transaction", "card", ["transferor_id"], ["id"])
    op.drop_constraint(
        "transaction_row_receiver_id_fkey",
        "transaction_row",
        type_="foreignkey",
    )
    op.drop_constraint(
        "transaction_row_transferor_id_fkey",
        "transaction_row",
        type_="foreignkey",
    )
    op.create_foreign_key(None, "transaction_row", "card", ["receiver_id"], ["id"])
    op.create_foreign_key(None, "transaction_row", "card", ["transferor_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "transaction_row", type_="foreignkey")
    op.drop_constraint(None, "transaction_row", type_="foreignkey")
    op.create_foreign_key(
        "transaction_row_transferor_id_fkey",
        "transaction_row",
        "wallet",
        ["transferor_id"],
        ["id"],
    )
    op.create_foreign_key(
        "transaction_row_receiver_id_fkey",
        "transaction_row",
        "wallet",
        ["receiver_id"],
        ["id"],
    )
    op.drop_constraint(None, "transaction", type_="foreignkey")
    op.drop_constraint(None, "transaction", type_="foreignkey")
    op.drop_constraint(None, "transaction", type_="foreignkey")
    op.create_foreign_key(
        "transaction_receiver_id_fkey",
        "transaction",
        "wallet",
        ["receiver_id"],
        ["id"],
    )
    op.create_foreign_key(
        "transaction_transferor_id_fkey",
        "transaction",
        "wallet",
        ["transferor_id"],
        ["id"],
    )
    op.create_foreign_key(
        "transaction_intermediary_id_fkey",
        "transaction",
        "wallet",
        ["intermediary_id"],
        ["id"],
    )
    # ### end Alembic commands ###
