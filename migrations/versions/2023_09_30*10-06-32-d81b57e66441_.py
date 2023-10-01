"""empty message

Revision ID: d81b57e66441
Revises: 4e3b3a3739c2
Create Date: 2023-09-30 10:06:32.806676

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d81b57e66441"
down_revision: Union[str, None] = "4e3b3a3739c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "pos",
        sa.Column("token", sa.String(), nullable=True),
        sa.Column("merchant_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchant.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pos_id"), "pos", ["id"], unique=True)
    op.create_index(op.f("ix_pos_token"), "pos", ["token"], unique=True)
    op.drop_index("ix_user_one_time_password", table_name="user")
    op.create_index(
        op.f("ix_user_one_time_password"),
        "user",
        ["one_time_password"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_user_one_time_password"), table_name="user")
    op.create_index(
        "ix_user_one_time_password",
        "user",
        ["one_time_password"],
        unique=False,
    )
    op.drop_index(op.f("ix_pos_token"), table_name="pos")
    op.drop_index(op.f("ix_pos_id"), table_name="pos")
    op.drop_table("pos")
    # ### end Alembic commands ###
