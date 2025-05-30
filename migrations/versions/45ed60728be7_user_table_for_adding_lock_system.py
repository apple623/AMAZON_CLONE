"""user table for adding lock system

Revision ID: 45ed60728be7
Revises: 
Create Date: 2025-05-17 00:37:34.230385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45ed60728be7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('faild_login_attempt', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('login_lock', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('login_lock')
        batch_op.drop_column('faild_login_attempt')

    # ### end Alembic commands ###
