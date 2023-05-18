import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
import yfinance as yf
from db_structure.sql_meta import StockMeta
from uuid import uuid4
import os
import requests
import pandas as pd
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime


class StockImporter:
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
    
    def login(self, uuid) -> bool:
        meta = self.meta
        findrow = meta.users.select().where(meta.users.c.id == uuid)
        with self.db.connect() as conn:
            res = conn.execute(findrow)
            try:
                return type(res.fetchone()[0]) == str
            except:
                return False
        
    def getMetaData(self, list) -> yf.Tickers:
        # Get metadata
        ticks = ' '.join(list)
        tickers = yf.Tickers(ticks)

        return tickers

    def handleCsv(self, file) -> pd.DataFrame:
        '''
        Returns a dataframe with the columns: date, description, isin, market, order_id, count
        '''

        df = pd.read_csv(file)

        df = df.loc[:, [ 'Datum'
                        ,'Product'
                        ,'ISIN'
                        ,'Beurs'
                        ,'Order ID'
                        ,'Aantal' ]]
        
        df.columns = [ 'date', 'description', 'isin' ,'market', 'order_id', 'count' ]

        self.cleaned_csv = df

        return df

    def get_stocks(self, user_id = None, df = None, by: List | str = ['description', 'ticker']):
        
        if user_id != None:
            with self.db.connect() as conn:
                stm = sa.sql.text("select si.*, su.count from share_info si inner join share_user su on si.id = su.share_id and coalesce(si.ticker, '') <> '' and su.user_id = :user_id ")
                
                stm = stm.bindparams(user_id=user_id)
                df = pd.read_sql(stm, con=conn)
        elif df == None:
            df = pd.DataFrame()

        meta = self.getMetaData(df['ticker'].unique())
        
        def TickerCurrentPrice(x):
            qte = self.get_saved_quote(x)
            if qte == None:
                try:
                    tk = meta.tickers[x].get_info()
                    return tk['currentPrice']
                except Exception: 
                    print(x)
                    return -10
            else:
                return qte

        df['Koers'] = df['ticker'].apply(lambda x: float(TickerCurrentPrice(x)))
        
        df['totalValue'] = (df['count'] * df['Koers'])
        
        if type(by) == str: by = [by]

        for it in by:
            if it not in df.columns:
                def getGrouping(x):
                    try:
                        return meta.tickers[x].info[it]
                    except KeyError:
                        return 'Other'
                df[it] = df['ticker'].apply(lambda x: getGrouping(x))


        df = df.groupby(
            by=by
        ).aggregate({
            'totalValue': 'sum',
            'count': 'sum'
        }).reset_index()

        df['percentage'] =  df['totalValue'] / sum(df['totalValue'])
        
        # Fix rounding
        df['totalValue'] = df['totalValue'].round(4)
        df['percentage'] = df['percentage'].round(4)

        return df

    def add_shares(self, file, userid = None):
        df = self.handleCsv(file)
        __share = self.meta.share_info

        df2 = df.loc[:, [ 'isin', 'description', 'market' ]]
        
        df2 = df2.drop_duplicates()
        

        df2.loc[:, 'id'] = [str(uuid4()) for _ in range(len(df2.index))]

        with self.db.connect() as conn:
            for row in df2.to_dict(orient='records'):
                stmt = insert(__share).values(row)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['isin', 'market']
                )
                conn.execute(stmt)
            conn.commit()
        
            sel = __share.select().where(__share.c.isin.in_(df['isin'])).where(__share.c.market.in_(df['market']))
            res = conn.execute(sel).fetchall()
        
            if userid != None:
                df3 = pd.merge(df, pd.DataFrame(res), how='left', left_on=['isin', 'market'], right_on=['isin', 'market'])
                df3['share_id'] = df3['id']
                df3['user_id'] = userid
                df3.loc[:, 'id'] = [str(uuid4()) for _ in range(len(df3.index))]
                df3 = df3.loc[:, [ 'id', 'share_id', 'order_id', 'user_id', 'count' ]]
                
                for row in df3.to_dict(orient='records'):
                    stmt = insert(self.meta.share_user).values(row)
                    stmt = stmt.on_conflict_do_nothing(
                        index_elements=['order_id']
                    )
                    conn.execute(stmt)
                conn.commit()

        return res
        
    def get_saved_quote(self, ticker: str) -> float | None:
        # We're gonna look into the database and fetch the last record
        stmt = sa.sql.text("""select sh.share_id, sh.price, sh.date, si.ticker, max(date) over(partition by ticker)
                                from share_history sh
                                left join share_info si on si.id = sh.share_id
                                where ticker = :ticker""")
        stmt.bindparams(ticker=ticker)
        
        with self.db.connect() as conn:
            res = conn.execute(stmt).fetchall()
        return pd.DataFrame(res)
            

    def get_last_quote(self, ticker):
        '''
        Get Quote data. If dev mode is on it will return a random number
        '''
        # Get random number if development mode is on
        if os.getenv('PYTHON_ENV') == 'development':
            from random import  SystemRandom
            return round(SystemRandom().uniform(50, 150), 4)
        
        # Refresh with new (hydrated) data
        else:
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={alphaVantageKey}'

            r = requests.get(url)
            data = r.json()

            try:
                return data['Global Quote']['05. price']
            except Exception as e:
                print(e)
                return None

    def get_prices(self):
        share_info = self.meta.share_info
        share_history = self.meta.share_history
        with Session(self.db) as sess:
            stm = sa.sql.select(share_info.c.id, share_info.c.ticker)
            res = sess.execute(stm).fetchall()
        
            df = pd.DataFrame(res)
            df['price'] = df['ticker'].apply(lambda x: self.get_last_quote(x))
            df['date'] = datetime.now()
            df['share_id'] = df['id']
            df['id'] = [str(uuid4()) for _ in range(len(df.index))]

            df = df.loc[:, ['id', 'share_id', 'price', 'date']]

            sess.execute(share_history.insert().values(df.to_dict(orient='records')))
            sess.commit()


        return 

