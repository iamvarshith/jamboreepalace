"""empty message

Revision ID: 186e6fd23613
Revises: f2b4cb9f8e1f
Create Date: 2021-05-05 01:21:51.846454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '186e6fd23613'
down_revision = 'f2b4cb9f8e1f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('property', 'contact_front',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
    op.alter_column('property', 'contact_manager',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
    op.alter_column('user', 'unique_id',
               existing_type=sa.VARCHAR(length=120),
               nullable='False')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'unique_id',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('property', 'contact_manager',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('property', 'contact_front',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    # ### end Alembic commands ###
