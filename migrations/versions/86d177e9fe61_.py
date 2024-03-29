"""empty message

Revision ID: 86d177e9fe61
Revises: aa7e8e2a772f
Create Date: 2021-05-07 13:17:37.262804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86d177e9fe61'
down_revision = 'aa7e8e2a772f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('property', sa.Column('rating', sa.Float(), nullable=True))
    op.alter_column('user', 'unique_id',
               existing_type=sa.VARCHAR(length=120),
               nullable='False')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'unique_id',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.drop_column('property', 'rating')
    # ### end Alembic commands ###
