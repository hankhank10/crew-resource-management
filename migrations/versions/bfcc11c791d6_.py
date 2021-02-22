"""empty message

Revision ID: bfcc11c791d6
Revises: 
Create Date: 2021-02-22 13:27:45.426290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bfcc11c791d6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('last_action', sa.DateTime(), nullable=True),
    sa.Column('join_date', sa.DateTime(), nullable=True),
    sa.Column('approved', sa.Boolean(), nullable=True),
    sa.Column('unique_setup_key', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
