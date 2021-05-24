"""initial revision

Revision ID: b692dfd0b017
Revises: 
Create Date: 2021-05-24 18:49:05.919157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b692dfd0b017'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('booking',
    sa.Column('job_id', sa.String(), nullable=False),
    sa.Column('product_feature', sa.String(), nullable=False),
    sa.Column('booked', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('job_id', 'product_feature')
    )
    op.create_table('license',
    sa.Column('product_feature', sa.String(), nullable=False),
    sa.Column('used', sa.Integer(), nullable=True),
    sa.Column('total', sa.Integer(), nullable=True),
    sa.CheckConstraint('used<=total'),
    sa.PrimaryKeyConstraint('product_feature')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('license')
    op.drop_table('booking')
    # ### end Alembic commands ###