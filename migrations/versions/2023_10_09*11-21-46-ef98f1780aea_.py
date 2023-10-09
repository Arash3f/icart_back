"""empty message

Revision ID: ef98f1780aea
Revises: 977ffc905904
Create Date: 2023-10-09 11:21:46.914524

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql

from alembic import op
import sqlalchemy as sa

from src.verify_phone.models import VerifyPhoneType

# revision identifiers, used by Alembic.
revision: str = "ef98f1780aea"
down_revision: Union[str, None] = "977ffc905904"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    verify_phone_type = postgresql.ENUM(VerifyPhoneType, name="verifyphonetype")
    verify_phone_type.create(op.get_bind(), checkfirst=True)
    op.add_column("verify_phone", sa.Column("type", verify_phone_type, nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    verify_phone_type = postgresql.ENUM(VerifyPhoneType, name="verifyphonetype")
    verify_phone_type.drop(op.get_bind())
    op.drop_column("verify_phone", "type")
    # ### end Alembic commands ###