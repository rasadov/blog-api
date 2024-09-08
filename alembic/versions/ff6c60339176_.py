"""empty message

Revision ID: ff6c60339176
Revises: 
Create Date: 2024-09-08 14:41:43.298917

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff6c60339176'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer, primary_key=True, index=True),
        sa.Column('username', sa.String, unique=True, index=True),
        sa.Column('email', sa.String, unique=True, index=True),
        sa.Column('password', sa.String)
    )

    op.create_table(
        'posts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('title', sa.String),
        sa.Column('content', sa.JSON),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.user_id'))
    )

def downgrade():
    op.drop_table('posts')
    op.drop_table('users')
