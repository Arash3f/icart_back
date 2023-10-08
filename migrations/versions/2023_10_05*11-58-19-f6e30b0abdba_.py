"""empty message

Revision ID: f6e30b0abdba
Revises: 41dbafc80bb0
Create Date: 2023-10-05 11:58:19.762776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f6e30b0abdba"
down_revision: Union[str, None] = "41dbafc80bb0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user",
        sa.Column("image_background_version_id", sa.String(), nullable=True),
    )
    op.add_column(
        "user",
        sa.Column("image_background_name", sa.String(), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "image_background_name")
    op.drop_column("user", "image_background_version_id")
    # ### end Alembic commands ###