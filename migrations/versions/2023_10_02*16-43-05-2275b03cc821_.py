"""empty message

Revision ID: 2275b03cc821
Revises: 67d2f57ec22d
Create Date: 2023-10-02 16:43:05.609281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2275b03cc821'
down_revision: Union[str, None] = '67d2f57ec22d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('organization', sa.Column('contract_number', sa.String(), nullable=True))
    op.add_column('organization', sa.Column('signatory_name', sa.String(), nullable=True))
    op.add_column('organization', sa.Column('signatory_position', sa.String(), nullable=True))
    op.add_column('organization', sa.Column('employees_number', sa.Integer(), nullable=True))
    op.add_column('organization', sa.Column('address', sa.TEXT(), nullable=True))
    op.add_column('organization', sa.Column('location_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'organization', 'location', ['location_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'organization', type_='foreignkey')
    op.drop_column('organization', 'location_id')
    op.drop_column('organization', 'address')
    op.drop_column('organization', 'employees_number')
    op.drop_column('organization', 'signatory_position')
    op.drop_column('organization', 'signatory_name')
    op.drop_column('organization', 'contract_number')
    # ### end Alembic commands ###
