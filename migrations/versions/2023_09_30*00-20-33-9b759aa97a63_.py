"""empty message

Revision ID: 9b759aa97a63
Revises: 2675d3d51702
Create Date: 2023-09-30 00:20:33.693983

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9b759aa97a63"
down_revision: Union[str, None] = "2675d3d51702"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ticket",
        sa.Column("title", sa.String(), nullable=True),
        sa.Column(
            "type",
            sa.Enum("TECHNICAL", "SALES", name="tickettype"),
            nullable=True,
        ),
        sa.Column(
            "position",
            sa.Enum("OPEN", "IN_PROGRESS", "CLOSE", name="ticketposition"),
            nullable=True,
        ),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ticket_code"), "ticket", ["code"], unique=True)
    op.create_index(op.f("ix_ticket_id"), "ticket", ["id"], unique=True)
    op.create_table(
        "ticket_message",
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("ticket_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["ticket.id"],
        ),
        sa.PrimaryKeyConstraint("creator_id", "id"),
    )
    op.create_index(op.f("ix_ticket_message_id"), "ticket_message", ["id"], unique=True)
    op.create_foreign_key(
        None,
        "agent",
        "user",
        ["agent_user_id"],
        ["id"],
        use_alter=True,
    )
    op.create_foreign_key(
        None,
        "organization",
        "user",
        ["user_organization_id"],
        ["id"],
        use_alter=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "organization", type_="foreignkey")
    op.drop_constraint(None, "agent", type_="foreignkey")
    op.drop_index(op.f("ix_ticket_message_id"), table_name="ticket_message")
    op.drop_table("ticket_message")
    op.drop_index(op.f("ix_ticket_id"), table_name="ticket")
    op.drop_index(op.f("ix_ticket_code"), table_name="ticket")
    op.drop_table("ticket")
    # ### end Alembic commands ###
