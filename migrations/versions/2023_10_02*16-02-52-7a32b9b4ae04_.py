"""empty message

Revision ID: 7a32b9b4ae04
Revises: 82c3f9850f1d
Create Date: 2023-10-02 16:02:52.928666

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "7a32b9b4ae04"
down_revision: Union[str, None] = "82c3f9850f1d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    post_status = postgresql.ENUM("USER", "SUPPORTER", name="ticketmessageposition")
    post_status.create(op.get_bind(), checkfirst=True)

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "ticket_message",
        sa.Column(
            "type",
            sa.Enum("USER", "SUPPORTER", name="ticketmessageposition"),
            nullable=False,
        ),
    )
    op.add_column(
        "ticket_message",
        sa.Column("user_status", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "ticket_message",
        sa.Column("supporter_status", sa.Boolean(), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    post_status = postgresql.ENUM("USER", "SUPPORTER", name="ticketmessageposition")
    post_status.drop(op.get_bind())

    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("ticket_message", "supporter_status")
    op.drop_column("ticket_message", "user_status")
    op.drop_column("ticket_message", "type")
    # ### end Alembic commands ###
