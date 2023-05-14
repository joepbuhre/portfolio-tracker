import sqlalchemy as sa

class StockMeta:
    def __init__(self):
        self.meta = sa.MetaData()
        
        self.__create_users__()
        self.__create_share_info__()
        self.__create_share_history__()

        return None

    def getMeta(self):
        return self

    def __create_users__(self):
        self.users = sa.Table('users', self.meta,
            sa.Column('ID', sa.VARCHAR(256), primary_key=True),
        )
        return 
    
    def __create_share_info__(self):
        self.share_info = sa.Table('share_info', self.meta,
                                   sa.Column('id', sa.VARCHAR(256), primary_key=True),
                                   sa.Column('Datum', sa.DATE),
                                   sa.Column('Tijd', sa.TIME),
                                   sa.Column('Product', sa.VARCHAR(256)),
                                   sa.Column('Beurs', sa.VARCHAR(256)),
                                   sa.Column('Uitvoeringsplaats', sa.VARCHAR(256)),
                                   sa.Column('OrderID', sa.VARCHAR(256))
                                   )
    
    def __create_share_history__(self):
        self.share_history = sa.Table('share_history', self.meta,
                                      sa.Column('id', sa.VARCHAR(256), primary_key=True),
                                      sa.Column('share_id', sa.VARCHAR(256)),
                                      sa.Column('price', sa.DECIMAL(19,4)) 
                                      )