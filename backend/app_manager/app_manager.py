import os
from uuid import uuid4
import sqlalchemy as sa
from db_structure.sql_meta import StockMeta

class AppManager:
    def __init__(self) -> None:
        self.db = sa.create_engine(os.environ.get('DB_STRING'))
        self.meta = StockMeta()

    def create_account(self, uuid = str(uuid4())) -> str:
        newrow = self.meta.users.insert()
        newrow = newrow.values(id=uuid)

        with self.db.connect() as conn:
            if conn.execute(self.meta.users.select().where(self.meta.users.c.id == uuid)).fetchone() == None:
                res = conn.execute(newrow)
                conn.commit()
        
        return uuid
    
    def login(self, uuid: str) -> bool:
        meta = self.meta
        findrow = meta.users.select().where(meta.users.c.id == uuid)
        with self.db.connect() as conn:
            res = conn.execute(findrow)
            try:
                return type(res.fetchone()[0]) == str
            except:
                return False