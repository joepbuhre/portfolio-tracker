import os
from uuid import uuid4
import sqlalchemy as sa
from db_structure import get_db
from db_structure.sql_meta import StockMeta
from sqlalchemy.orm import Session

class AppManager:
    def __init__(self) -> None:
        self.db = get_db()
        self.meta = StockMeta()

    def create_account(self, uuid = str(uuid4())) -> str:
        newrow = self.meta.users.insert()
        newrow = newrow.values(id=uuid)

        with self.db.connect() as sess:
            if sess.execute(self.meta.users.select().where(self.meta.users.c.id == uuid)).fetchone() == None:
                res = sess.execute(newrow)
                sess.commit()
        
        return uuid
    
    def login(self, uuid: str) -> bool:
        meta = self.meta
        findrow = meta.users.select().where(meta.users.c.id == uuid)
        with self.db.connect() as sess:
            res = sess.execute(findrow)
            try:
                return type(res.fetchone()[0]) == str
            except:
                return False