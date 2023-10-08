"""empty message

Revision ID: 751be9ad62fe
Revises: 498557937a12
Create Date: 2023-10-08 08:53:45.395037

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "751be9ad62fe"
down_revision: Union[str, None] = "498557937a12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_verify_phone_verify_code", table_name="verify_phone")
    op.create_index(
        op.f("ix_verify_phone_verify_code"),
        "verify_phone",
        ["verify_code"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_verify_phone_verify_code"), table_name="verify_phone")
    op.create_index(
        "ix_verify_phone_verify_code",
        "verify_phone",
        ["verify_code"],
        unique=False,
    )
    # ### end Alembic commands ###