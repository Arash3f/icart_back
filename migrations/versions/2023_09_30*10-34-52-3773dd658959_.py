"""empty message

Revision ID: 3773dd658959
Revises: d81b57e66441
Create Date: 2023-09-30 10:34:52.936459

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3773dd658959"
down_revision: Union[str, None] = "d81b57e66441"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "card",
        sa.Column("number", sa.String(), nullable=True),
        sa.Column("cvv2", sa.Integer(), nullable=False),
        sa.Column("expiration_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("dynamic_password", sa.Integer(), nullable=True),
        sa.Column("dynamic_password_exp", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "type",
            sa.Enum("CREDIT", "GOLD", "BLUE", "PLATINUM", name="cardenum"),
            nullable=False,
        ),
        sa.Column("wallet_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["wallet_id"],
            ["wallet.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_card_id"), "card", ["id"], unique=True)
    op.create_index(op.f("ix_card_number"), "card", ["number"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_card_number"), table_name="card")
    op.drop_index(op.f("ix_card_id"), table_name="card")
    op.drop_table("card")
    # ### end Alembic commands ###
