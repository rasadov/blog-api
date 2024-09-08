"""empty message

Revision ID: 447886dc3e2e
Revises: ff6c60339176
Create Date: 2024-09-09 01:18:00.536049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '447886dc3e2e'
down_revision: Union[str, None] = 'ff6c60339176'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('image_url', sa.String))


def downgrade() -> None:
    op.drop_column('posts', 'image_url')
