"""empty message

Revision ID: 8ad23b4733c8
Revises: 4a45729ce758
Create Date: 2023-10-16 14:41:50.119652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8ad23b4733c8"
down_revision: Union[str, None] = "4a45729ce758"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "merchant",
        sa.Column(
            "selling_type",
            sa.Enum("CASH", "CREDIT", "BOTH", name="sellingtype"),
            nullable=True,
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("merchant", "selling_type")
    # ### end Alembic commands ###