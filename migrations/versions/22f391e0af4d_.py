"""empty message

Revision ID: 22f391e0af4d
Revises: ba6f10311398
Create Date: 2020-03-12 17:26:13.168905

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22f391e0af4d'
down_revision = 'ba6f10311398'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.execute('''
        UPDATE artists
           SET created_at = %s
         WHERE created_at IS NULL;
    ''' % sa.func.now())
    op.alter_column('artists', 'created_at', nullable=False)
    op.add_column('venues', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.execute('''
        UPDATE venues
           SET created_at = %s
         WHERE created_at IS NULL;
    ''' % sa.func.now())
    op.alter_column('venues', 'created_at', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'created_at')
    op.drop_column('artists', 'created_at')
    # ### end Alembic commands ###
