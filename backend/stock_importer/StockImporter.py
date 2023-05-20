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
        
        df['Koers'] = df['ticker'].apply(lambda x: float(self.get_saved_quote(x)))
        
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

        # Remove unneeded rows
        df = df[df['count'] > 0]

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
        stmt = sa.sql.text("""select price
                                from (
                                    select sh.share_id, sh.price, sh.date, si.ticker, max(date) over(partition by ticker)
                                    from share_history sh
                                    left join share_info si on si.id = sh.share_id
                                ) t
                                where t.max = t.date and ticker = :ticker""")
        stmt = stmt.bindparams(ticker=ticker)

        with self.db.connect() as conn:
            res = conn.execute(stmt).fetchone()
        return res[0]

    def get_last_quote(self, ticker):
        '''
        Get Quote data. If dev mode is on it will return a random number
        '''
        price = None
        # Get random number if development mode is on
        if os.getenv('PYTHON_ENV') == 'development':
            from random import  SystemRandom
            price = round(SystemRandom().uniform(50, 150), 4)
        
        # Refresh with new (hydrated) data
        else:
            key = os.getenv('alphaVantageKey')
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={key}'

            r = requests.get(url)
            data = r.json()
    	
            try:
                price = float(data['Global Quote']['05. price'])
            except Exception as e:
                print(e)
                price = None
        
        if price == None:
            tick = yf.Ticker(ticker)
            try:
                price = float(tick.get_info()['currentPrice'])
            except Exception as e: 
                print(e)
                price = None
        
        return price

    def set_prices(self):
        share_history = self.meta.share_history
        with Session(self.db) as sess:
            stm = sa.sql.text("""select *
                                    from (
                                        select si.id as share_id, sh.price, sh.date, si.ticker, max(date) over(partition by ticker)
                                        from share_info si
                                        left join share_history sh on si.id = sh.share_id
                                    ) t
                                    where coalesce(date, now()) = coalesce(date, now())
                                    order by date asc
                                    limit 4""")
            
            res = sess.execute(stm).fetchall()
        
            df = pd.DataFrame(res)
            df['price'] = df['ticker'].apply(lambda x: self.get_last_quote(x))
            df['date'] = datetime.now()
            df['id'] = [str(uuid4()) for _ in range(len(df.index))]

            df = df.dropna()
            if df.empty == False:
                df2 = df.loc[:, ['id', 'share_id', 'price', 'date']]
                sess.execute(share_history.insert().values(df2.to_dict(orient='records')))
                sess.commit()
            else:
                print('df is empty')
            

        return df.to_dict(orient='records')

    def get_history(self, tickers: List = None, userid: str = None):
        if userid != None:
            sel = sa.sql.text("""select *, ROUND(CASE WHEN COALESCE(prev_price, 0) = 0 THEN 0 ELSE price / prev_price -1 END, 4) AS growth from (
                                    select sh.id, sh.share_id, sh.price, sh.date, si.ticker, lag(sh.price) over (partition by sh.share_id order by sh.date asc) prev_price
                                    from share_history sh
                                    left join share_info si on sh.share_id = si.id
                                    where share_id 
                                        in ( select share_id from share_user where user_id = :userid ) 
                                        and si.ticker is not null
                                        and sh.price is not null
                                ) t """)
            sel = sel.bindparams(userid=userid)

        else :
            sel = sa.sql.text("""select sh.id, sh.share_id, sh.price, sh.date, si.ticker
                                from share_history sh
                                left join share_info si on sh.share_id = si.id
                                where ticker in :tickers""")
            sel = sel.bindparams(tickers=tuple(tickers))
            

        with self.db.connect() as conn:
            res = conn.execute(sel).fetchall()
        df = pd.DataFrame(res)
        tickdic = {}
        for ticker in df['ticker'].unique():
            tickdic[ticker] = df[df['ticker'] == ticker].to_dict(orient='records')
                    
        return tickdic