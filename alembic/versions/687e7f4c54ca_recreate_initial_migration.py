"""Recreate initial migration

Revision ID: 687e7f4c54ca
Revises: 
Create Date: 2025-03-21 17:41:33.176364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '687e7f4c54ca'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('leads',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('company', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('stage', sa.String(), nullable=True),
    sa.Column('engaged', sa.Boolean(), nullable=True),
    sa.Column('last_contacted', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_leads_email'), 'leads', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_leads_email'), table_name='leads')
    op.drop_table('leads')
    # ### end Alembic commands ###
