from os import getenv
from dotenv import load_dotenv
from sqlalchemy import create_engine


def get_db():
    load_dotenv()
    engine = create_engine(
        url = getenv('DB_STRING'), pool_size=20, max_overflow=0
    )
    return engine

