"""empty message

Revision ID: 20b9db591fba
Revises: 0c9a29ed8cf0
Create Date: 2023-09-30 01:31:19.231033

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20b9db591fba"
down_revision: Union[str, None] = "0c9a29ed8cf0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "agent_location",
        sa.Column("agent_id", sa.UUID(), nullable=True),
        sa.Column("location_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agent.id"],
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["location.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_location_id"), "agent_location", ["id"], unique=True)
    op.drop_constraint("location_agent_id_fkey", "location", type_="foreignkey")
    op.drop_column("location", "agent_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "location",
        sa.Column("agent_id", sa.UUID(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "location_agent_id_fkey",
        "location",
        "agent",
        ["agent_id"],
        ["id"],
    )
    op.drop_index(op.f("ix_agent_location_id"), table_name="agent_location")
    op.drop_table("agent_location")
    # ### end Alembic commands ###
