"""empty message

Revision ID: 498557937a12
Revises: 7cc7bea0801e
Create Date: 2023-10-05 12:32:19.484384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "498557937a12"
down_revision: Union[str, None] = "7cc7bea0801e"
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
        sa.ForeignKeyConstraint(["agent_id"], ["agent.id"]),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_location_id"), "agent_location", ["id"], unique=True)
    op.add_column("organization", sa.Column("location_id", sa.UUID(), nullable=True))
    op.create_foreign_key(None, "organization", "location", ["location_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "organization", type_="foreignkey")
    op.drop_column("organization", "location_id")
    op.drop_index(op.f("ix_agent_location_id"), table_name="agent_location")
    op.drop_table("agent_location")
    # ### end Alembic commands ###