"""delete openai key

Revision ID: 428e5b19e5de
Revises: 9b92c190bb61
Create Date: 2023-10-08 00:06:31.077871

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '428e5b19e5de'
down_revision = '9b92c190bb61'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('cle_api_openai')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cle_api_openai', sa.VARCHAR(length=255), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
