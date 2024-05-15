"""empty message

Revision ID: 65ffded39fbd
Revises: 0857ddae7997
Create Date: 2024-04-22 08:14:44.420635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65ffded39fbd'
down_revision = '0857ddae7997'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_name', sa.String(length=255), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.drop_column('product_name')

    # ### end Alembic commands ###