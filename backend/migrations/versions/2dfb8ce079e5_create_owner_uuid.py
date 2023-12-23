"""Create owner UUID

Revision ID: 2dfb8ce079e5
Revises: ef227d66b2c3
Create Date: 2023-12-23 20:59:32.162375

"""
from os import getenv
from typing import Sequence, Union

from alembic import op
from db_structure import get_db
from db_structure.model import User
import sqlalchemy as sa
from sqlalchemy.orm import Session
from utils.exceptions import NotExistException


# revision identifiers, used by Alembic.
revision: str = '2dfb8ce079e5'
down_revision: Union[str, None] = 'ef227d66b2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    userid = getenv('OWNER_GUID')
    if userid == None:
        raise NotExistException("Owner GUID is Missing!")

    with Session(get_db()) as conn:
        conn.add(
            User( id = userid)
        )
        conn.commit()
    pass


def downgrade() -> None:
    pass
