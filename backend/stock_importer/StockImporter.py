import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
import yfinance as yf
from backend.utils.yfinance_session import get_session
from db_structure.sql_meta import StockMeta
from uuid import uuid4
import os
import requests
import pandas as pd
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.dialects import postgresql as pg


class StockImporter:
    def __init__(self) -> None:
        self.db = sa.create_engine(os.environ.get('DB_STRING'))
        self.meta = StockMeta()
        self.session = get_session()

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
        print('still working')
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

    def get_share_info(self, user_id = None, df = None, by: List | str = ['description', 'ticker']):
        with self.db.connect() as conn:
            stmt = self.meta.share_info.select()
            res = conn.execute(stmt).fetchall()
        
        return pd.DataFrame(res).to_dict(orient='records')

    def get_stocks(self, user_id = None, df = None, by: List | str = ['description', 'ticker']):
        
        if user_id != None:
            with self.db.connect() as conn:
                stm = sa.sql.text("select si.*, su.count from share_info si inner join share_user su on si.id = su.share_id and coalesce(si.ticker, '') <> '' and su.user_id = :user_id ")
                
                stm = stm.bindparams(user_id=user_id)
                df = pd.read_sql(stm, con=conn)
                print(df)
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

    def match_ticker(self, shareid_ticker: list[dict]):
        shares = self.meta.share_info
        with self.db.connect() as conn:
            for row in shareid_ticker:
                stmt = shares.update().where(shares.c.id == row['share_id']).values(ticker=row['ticker'])            
                conn.execute(stmt)
            conn.commit()

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
        if res == None:
            return 0
        else:
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
            stm = sa.sql.text("""select si.ticker,si.id as share_id
                                    from share_info si
                                    left join share_history sh on si.id = sh.share_id
                                    group by si.id, si.ticker
                                    order by max(coalesce(sh.date, '1900-01-01')) asc
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

    def set_history(self, ticker: str):
        with self.db.connect() as conn:
            stm = sa.sql.text("""select id from share_info where ticker = :ticker""")
            stm = stm.bindparams(ticker=ticker)

            res = conn.execute(stm).fetchone()
            share_id = res[0]
            
            tick = yf.Ticker(ticker, self.session)
            res = tick.history(start='2023-09-01', end='2023-09-30')
            res.columns = ['open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits']

            res['date'] = res.index
            res['share_id'] = share_id
            res.loc[:, 'id'] = [str(uuid4()) for _ in range(len(res.index))]

            res = res.to_dict(orient='records') 

            # stm = si.meta.config.insert()
            stmt = pg.insert(self.meta.share_history).values(
                res
            )
            # stmt = stmt.on_conflict_do_update(
            #     constraint=self.meta.config.primary_key, 
            #     set_={'key': 'reset_token', 'value': token}

            # )
            stmt = stmt.on_conflict_do_nothing()
            conn.execute(stmt)
            conn.commit()

        return res 

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
        if df.empty:
            return tickdic
        else:
            for ticker in df['ticker'].unique():
                tickdic[ticker] = df[df['ticker'] == ticker].to_dict(orient='records')
                    
            return tickdic
