import sqlalchemy as sa
import os

class StockMeta:
    def __init__(self):
        self.meta = sa.MetaData()
        
        self.__create_users__()
        self.__create_share_info__()
        self.__create_share_history__()
        self.__create_share_user__()
        self.__create_config__()

        return None

    def getMeta(self):
        return self

    def manual_scripts(self):
        return """
        create unique index IF NOT EXISTS x_share_info_unique on share_info (isin);    
        -- create unique index IF NOT EXISTS x_share_user_unique_hash on share_user (hash);    
        create unique index IF NOT EXISTS x_share_history_unique on share_history (share_id, date);
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
                                    sa.Column('user_id', sa.VARCHAR(256), nullable=False),
                                    sa.Column('purchase_date', sa.DateTime),
                                    sa.Column('currency_date', sa.Date),
                                    sa.Column('product', sa.VARCHAR(500), nullable=True),
                                    sa.Column('isin', sa.VARCHAR(256)),
                                    sa.Column('description', sa.VARCHAR(500), nullable=True),
                                    sa.Column('fxrate', sa.DECIMAL(19,4), default=0),
                                    sa.Column('mutation_currency', sa.VARCHAR(20), nullable=True),
                                    sa.Column('mutation', sa.DECIMAL(19,4), default=0),
                                    sa.Column('balance_currency', sa.VARCHAR(20), nullable=True),
                                    sa.Column('balance', sa.DECIMAL(19,4), default=0),
                                    sa.Column('order_id', sa.VARCHAR(256), nullable=True),
                                    sa.Column('quantity', sa.DECIMAL(19,4), nullable=True),
                                    sa.Column('share_price', sa.DECIMAL(19,4), nullable=True),
                                    sa.Column('hash', sa.Numeric, unique=True),
                                   )
    def __create_share_history__(self):
        self.share_history = sa.Table('share_history', self.meta,
                                      sa.Column('id', sa.VARCHAR(256), primary_key=True),
                                      sa.Column('share_id', sa.VARCHAR(256)),
                                      sa.Column('open', sa.DECIMAL(19,4)),
                                      sa.Column('close', sa.DECIMAL(19,4)),
                                      sa.Column('low', sa.DECIMAL(19,4)),
                                      sa.Column('high', sa.DECIMAL(19,4)),
                                      sa.Column('volume', sa.DECIMAL(19,4)),
                                      sa.Column('dividends', sa.DECIMAL(19,4)),
                                      sa.Column('stock_splits', sa.DECIMAL(19,4)),
                                      sa.Column('date', sa.DateTime),
                                      )
    def __create_config__(self):
        self.config = sa.Table('config', self.meta,
                               sa.Column('key', sa.VARCHAR(256), primary_key=True),
                               sa.Column('value', sa.VARCHAR(None)),
                               )