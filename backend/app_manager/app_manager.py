import os
from uuid import uuid4
import sqlalchemy as sa
from db_structure import get_db
from db_structure.model import ShareActions, ShareHistory, ShareInfo, User
from sqlalchemy.orm import Session

class AppManager:
    def __init__(self) -> None:
        self.db = get_db()

    def create_account(self, uuid = str(uuid4())) -> str:
        newrow = sa.insert(User)
        newrow = newrow.values(id=uuid)

        with self.db.connect() as sess:
            if sess.execute(sa.select(User).where(User.id == uuid)).fetchone() == None:
                res = sess.execute(newrow)
                sess.commit()
        
        return uuid
    
    def login(self, uuid: str) -> bool:
        findrow = sa.select(User).where(User.id == uuid)
        with self.db.connect() as sess:
            res = sess.execute(findrow)
            try:
                return type(res.fetchone()[0]) == str
            except:
                return False