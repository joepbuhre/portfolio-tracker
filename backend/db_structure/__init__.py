from os import getenv
from sqlalchemy import create_engine


def get_db():
    engine = create_engine(
        url = getenv('DB_STRING'), pool_size=20, max_overflow=0
    )
    return engine

