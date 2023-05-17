import sqlalchemy as sa
import os

class StockMeta:
    def __init__(self):
        self.meta = sa.MetaData()
        
        self.__create_users__()
        self.__create_share_info__()
        self.__create_share_history__()
        self.__create_share__()
        self.__create_share_user__()

        return None

    def getMeta(self):
        return self

    def manual_scripts(self):
        return """
        create unique index IF NOT EXISTS x_share_info_unique on share_info (isin, market);    
        create unique index IF NOT EXISTS x_share_user_unique_order_id on share_user (order_id);    
        """

    def __create_users__(self):
        self.users = sa.Table('users', self.meta,
            sa.Column('id', sa.VARCHAR(256), primary_key=True),
        )
        return 
    
    def __create_share_info__(self):
        self.share_info = sa.Table('share_info', self.meta,
                                   sa.Column('id', sa.VARCHAR(256), primary_key=True),
                                   sa.Column('isin', sa.VARCHAR(256)),
                                   sa.Column('description', sa.VARCHAR(256)),
                                   sa.Column('market', sa.VARCHAR(256)),
                                   sa.Column('ticker', sa.VARCHAR(256)),
                                   )
    def __create_share_user__(self):
        self.share_user = sa.Table('share_user', self.meta,
                                    sa.Column('id', sa.VARCHAR(256), primary_key=True),
                                    sa.Column('share_id', sa.VARCHAR(256)),
                                    sa.Column('order_id', sa.VARCHAR(256)),
                                    sa.Column('user_id', sa.VARCHAR(256), nullable=False),
                                    sa.Column('count', sa.Numeric, default=0)
                                   )
       
    def __create_share_history__(self):
        self.share_history = sa.Table('share_history', self.meta,
                                      sa.Column('id', sa.VARCHAR(256), primary_key=True),
                                      sa.Column('share_id', sa.VARCHAR(256)),
                                      sa.Column('price', sa.DECIMAL(19,4)),
                                      sa.Column('user_id', sa.VARCHAR(256)),
                                      )
    def __create_share__(self):
        self.share = sa.Table('share', self.meta,
                              sa.Column('id', sa.VARCHAR(256), primary_key=True),
                              sa.Column('isin', sa.VARCHAR(256), nullable=False),
                              sa.Column('order_id', sa.VARCHAR(256)),
                              sa.Column('stock_market', sa.VARCHAR(256)),
                              sa.Column('user_id', sa.VARCHAR(256), nullable=False),
                              )