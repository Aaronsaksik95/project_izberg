"""empty message

Revision ID: ffe854bc8ae8
Revises: a17247d666b1
Create Date: 2021-01-28 17:27:40.312301

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffe854bc8ae8'
down_revision = 'a17247d666b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'game', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'game', type_='unique')
    # ### end Alembic commands ###