from datetime import datetime
from hmac import new
import os
from turtle import home
import numpy as np
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from db_structure import get_db
from utils.yfinance_session import get_session
from db_structure.sql_meta import StockMeta


class DeGiro:
    def __init__(self) -> None:
        self.db = get_db()
        self.meta = StockMeta()
        self.session = get_session()
    
    def parse_action(self, x):
        if x['isin'] == 'NLFLATEXACNT':
            return 'Geld gestort'
        if x['quantity'] is not None:
            return 'Koop'
        return None

    def parse_test(self, x: pd.DataFrame):
        quantity = x.loc[x['quantity'].notnull(), 'quantity'].values ,
        transaction_cost = x.loc[x['description'] == 'DEGIRO Transactiekosten en/of kosten van derden', 'mutation'].values ,
        foreign_mutation = sum(x.loc[:, 'mutation'].values) ,
        home_mutation = x.loc[x['description'] == 'Valuta Debitering', 'mutation'].values ,
        fx_rate = x.loc[x['fxrate'].notnull(), 'fxrate'].values ,
        description = x.loc[:, 'description'].values

        quantity = list(quantity[0]) if len(quantity[0]) > 0 else [None]
        transaction_cost = list(transaction_cost[0]) if len(transaction_cost[0]) > 0 else [None]
        foreign_mutation = list(foreign_mutation) if foreign_mutation else [None]
        home_mutation = list(home_mutation[0]) if len(home_mutation[0]) > 0 else [None]
        fx_rate = list(fx_rate[0]) if len(fx_rate[0]) > 0 else [None]
        description = [description[0]] if len(description[0]) > 0 else [None]
                
        new_df = pd.DataFrame({
            'purchase_date': pd.Timestamp(x['purchase_date'].values[0]).date().strftime('%Y-%m-%d'),
            'order_id': x['order_id'].values[0],
            'share_id': x['share_id'].values[0],
            'description': description,
            'quantity': quantity, 
            'transaction_cost': transaction_cost, 
            'foreign_mutation': foreign_mutation if fx_rate[0] is not None else None, 
            'home_mutation': foreign_mutation if fx_rate[0] is None else home_mutation, 
            'fx_rate': fx_rate, 
        })
        return new_df

    def get_account(self):
        with Session(self.db) as sess:
            stm = text("select * from share_user where user_id = :user_id").bindparams(user_id=os.environ.get('OWNER_GUID'))
            res = sess.execute(stm).fetchall()
            df = pd.DataFrame(res)
            if df.empty == True:
                return []
            df = df[df['share_id'].notnull()]

            # df = df[df['share_id'] == '63f6ce83-2742-4dfd-a6b1-c881d2b35658']

            df['action'] = df.apply(self.parse_action, axis=1)

            df = df.groupby(['purchase_date','order_id', 'share_id'], as_index=False, dropna=False).apply(self.parse_test)#.reset_index()

            shares = pd.DataFrame(
                sess.execute(
                    text("select * from share_info")
                ).fetchall()
            )

            df = df.merge(right=shares, how='left',left_on='share_id', right_on='id', suffixes=[None, '_share'])

            sess.close()

        return df.to_dict(orient='records')
        