"""empty message

Revision ID: 7cc7bea0801e
Revises: f1ce20793d82
Create Date: 2023-10-05 12:24:59.167164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "7cc7bea0801e"
down_revision: Union[str, None] = "f1ce20793d82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_agent_location_id", table_name="agent_location")
    op.drop_table("agent_location")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "agent_location",
        sa.Column("agent_id", sa.UUID(), autoincrement=False, nullable=True),
        sa.Column("location_id", sa.UUID(), autoincrement=False, nullable=True),
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agent.id"],
            name="agent_location_agent_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["location.id"],
            name="agent_location_location_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="agent_location_pkey"),
    )
    op.create_index("ix_agent_location_id", "agent_location", ["id"], unique=False)
    # ### end Alembic commands ###
