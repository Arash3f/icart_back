"""empty message

Revision ID: f1ce20793d82
Revises: f6e30b0abdba
Create Date: 2023-10-05 12:20:51.956223

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f1ce20793d82"
down_revision: Union[str, None] = "f6e30b0abdba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("agent", sa.Column("user_id", sa.UUID(), nullable=True))
    op.drop_constraint("agent_agent_user_id_fkey", "agent", type_="foreignkey")
    op.create_foreign_key(None, "agent", "user", ["user_id"], ["id"], use_alter=True)
    op.drop_column("agent", "agent_user_id")
    op.add_column("organization", sa.Column("user_id", sa.UUID(), nullable=True))
    op.drop_constraint(
        "organization_location_id_fkey",
        "organization",
        type_="foreignkey",
    )
    op.drop_constraint(
        "organization_user_organization_id_fkey",
        "organization",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "organization",
        "user",
        ["user_id"],
        ["id"],
        use_alter=True,
    )
    op.drop_column("organization", "location_id")
    op.drop_column("organization", "user_organization_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "organization",
        sa.Column(
            "user_organization_id",
            sa.UUID(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "organization",
        sa.Column("location_id", sa.UUID(), autoincrement=False, nullable=True),
    )
    op.drop_constraint(None, "organization", type_="foreignkey")
    op.create_foreign_key(
        "organization_user_organization_id_fkey",
        "organization",
        "user",
        ["user_organization_id"],
        ["id"],
    )
    op.create_foreign_key(
        "organization_location_id_fkey",
        "organization",
        "location",
        ["location_id"],
        ["id"],
    )
    op.drop_column("organization", "user_id")
    op.add_column(
        "agent",
        sa.Column("agent_user_id", sa.UUID(), autoincrement=False, nullable=True),
    )
    op.drop_constraint(None, "agent", type_="foreignkey")
    op.create_foreign_key(
        "agent_agent_user_id_fkey",
        "agent",
        "user",
        ["agent_user_id"],
        ["id"],
    )
    op.drop_column("agent", "user_id")
    # ### end Alembic commands ###