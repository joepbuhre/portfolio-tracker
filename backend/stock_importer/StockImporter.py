from sys import prefix
from app.types.degiro import categorize_transaction
from db_structure.model import ShareActions
import numpy as np
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
import yfinance as yf
from db_structure import get_db
from utils.degiro import extract_description
from utils.exceptions import NotExistException
from utils.helpers import set_hash, set_uuid
from utils.yfinance_session import get_session
from db_structure.model import ShareHistory, ShareActions, ShareInfo
from uuid import uuid4
import os
import requests
import pandas as pd
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.dialects import postgresql as pg
from utils.logger import log


class StockImporter:
    def __init__(self, userid) -> None:
        self.db = get_db()
        self.session = get_session()
        self.userid = userid

    def getMetaData(self, list) -> yf.Tickers:
        # Get metadata
        ticks = ' '.join(list)
        tickers = yf.Tickers(ticks, session=self.session)

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
    
    def handleCsvAccount(self, file) -> pd.DataFrame:
        '''
        Returns a dataframe with the columns: date, description, isin, market, order_id, count
        '''

        df = pd.read_csv(file)

        df.columns = [   'date'
                        ,'time'
                        ,'currency_date'
                        ,'product'
                        ,'isin'
                        ,'description'
                        ,'fxrate'
                        ,'mutation_currency'
                        ,'mutation'
                        ,'balance_currency'
                        ,'balance'
                        ,'order_id']

        self.cleaned_csv = df
        try:
            df['purchase_date'] = pd.to_datetime((df['date'] + ' ' + df['time']), format='%d-%m-%Y %H:%M')
            df['currency_date'] = pd.to_datetime(df['currency_date'], format='%d-%m-%Y')
            df.drop(columns=['date', 'time'], inplace=True)

            df = df.replace({np.nan: None})
        except Exception as e:
            print(e)
        
        return df
    
    def handleCsvAccountV2(self, file) -> pd.DataFrame:
        '''
        Returns a dataframe with the columns: date, description, isin, market, order_id, count
        '''

        df = pd.read_csv(file)

        df.columns = [   'date'
                        ,'time'
                        ,'currency_date'
                        ,'product'
                        ,'isin'
                        ,'description'
                        ,'fxrate'
                        ,'mutation_currency'
                        ,'mutation'
                        ,'balance_currency'
                        ,'balance'
                        ,'order_id']

        self.cleaned_csv = df
        try:
            df['purchase_date'] = pd.to_datetime((df['date'] + ' ' + df['time']), format='%d-%m-%Y %H:%M')
            df['currency_date'] = pd.to_datetime(df['currency_date'], format='%d-%m-%Y')
            df.drop(columns=['date', 'time'], inplace=True)


            df['action'] = df['description'].astype(str).apply(lambda x: categorize_transaction(x))

            df = df.replace({np.nan: None})

            df = df.loc[:, [
                'currency_date',
                'product',
                'description',
                'isin',
                'fxrate',
                'mutation_currency',
                'mutation',
                'order_id',
                'purchase_date',
                'action'
            ]]

            df = df[df['mutation'].notnull()]

        except Exception as e:
            print(e)
        
        return df
    
    def get_share_info(self, user_id = None, df = None, by: List | str = ['description', 'ticker']):
        with self.db.connect() as conn:
            stmt = sa.select(ShareInfo)
            res = conn.execute(stmt).fetchall()
        
        return pd.DataFrame(res).to_dict(orient='records')

    def get_stocks(self, user_id = None, df = None, by: List | str = ['description', 'ticker']):
        
        if user_id != None:
            with self.db.connect() as conn:
                stm = sa.sql.text("""
select si.* , SUM(case when su.mutation < 0 then su.quantity else -su.quantity end) as quantity
from share_info si 
inner join share_user su on si.id = su.share_id and coalesce(si.ticker, '') <> '' and su.user_id = :user_id 
group by si.id, si.isin, si.description,si.market, si.ticker
                                  """)
                
                stm = stm.bindparams(user_id=user_id)
                df = pd.read_sql(stm, con=conn)
        elif df == None:
            df = pd.DataFrame()

        meta = self.getMetaData(df['ticker'].unique())
        
        df['Koers'] = df['ticker'].apply(lambda x: float(self.get_saved_quote(x)))
        
        df['totalValue'] = (df['quantity'] * df['Koers'])
        
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
            'quantity': 'sum'
        }).reset_index()

        df['percentage'] =  df['totalValue'] / sum(df['totalValue'])
        
        # Fix rounding
        df['totalValue'] = df['totalValue'].round(4)
        df['percentage'] = df['percentage'].round(4)

        # Remove unneeded rows
        df = df[df['quantity'] > 0]

        return df

    def add_shares(self, file):
        df = self.handleCsvAccountV2(file)
        userid = self.userid

        # first insert the possible new tickers we've got
        # we need to check how we are going to set market
        df_stocks = df.loc[:, [ 'isin', 'product' ]]
        df_stocks.columns = ['isin', 'description']
        df_stocks = df_stocks.drop_duplicates(subset=['isin']).dropna()
        df_stocks = set_uuid(df_stocks)

        with self.db.connect() as conn:
            for row in df_stocks.to_dict(orient='records'):
                stmt = insert(ShareInfo).values(row)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['isin']
                )
                conn.execute(stmt)
            conn.commit()
        
            sel = sa.select(ShareInfo).where(ShareInfo.isin.in_(df['isin']))
            res = conn.execute(sel).fetchall()
        
            if userid != None:
                df3 = pd.merge(df, pd.DataFrame(res).loc[:, ['isin', 'id']], how='left', left_on=['isin'], right_on=['isin'])
                df3['share_id'] = df3['id']
                df3['user_id'] = userid
                df3 = set_uuid(df3)
                df3 = extract_description(df3)
                df3 = df3.replace({np.nan: None})


                # df3 = df3.loc[:, [ 'id', 'share_id', 'order_id', 'user_id', 'count' ]]
                
                df3 = df3.loc[:, ['id','user_id','share_id','purchase_date','currency_date','product','fxrate','isin','mutation_currency','mutation','order_id','action','quantity','share_price']]
                
                stmt = insert(ShareActions).values(df3.to_dict(orient='records')).on_conflict_do_nothing(
                    index_elements=['purchase_date', 'share_id', 'isin', 'action', 'order_id']
                )
                conn.execute(stmt)
                conn.commit()

        return True 

    def match_ticker(self, shareid_ticker: list[dict]):
        with self.db.connect() as conn:
            for row in shareid_ticker:
                stmt = sa.update(ShareInfo).where(ShareInfo.id == row['share_id']).values(ticker=row['ticker'])            
                conn.execute(stmt)
            conn.commit()

    def get_saved_quote(self, ticker: str) -> float | None:
        # We're gonna look into the database and fetch the last record
        stmt = sa.sql.text("""
select case when curr.currency = 'USD' then t.price / t.fxrate else price end as price, *
from (
	select sh.share_id, sh.close as price, sh.date, si.ticker, max(sh.date) over(partition by ticker), exchange.close as fxrate
	from share_history sh
	left join share_info si on si.id = sh.share_id
	left join (
		select * from share_history where share_id = (select id from share_info where ticker = 'EURUSD=X')
	) exchange on sh.date::date = exchange.date::date
) t
left join (
	select share_id, min(mutation_currency) as currency 
	from share_user 
	where quantity is not null 
	group by share_id
) curr on curr.share_id = t.share_id
where t.max = t.date and ticker = :ticker
""")
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
                sess.execute(sa.insert(ShareHistory).values(df2.to_dict(orient='records')))
                sess.commit()
            else:
                print('df is empty')
            

        return df.to_dict(orient='records')

    def set_history(self, ticker: List[str] | bool, save: bool, time_period: None | dict) -> list:
        with self.db.connect() as conn:
            # Fetch share ID
            share_ids = conn.execute(
                sa.sql.text("""select id, ticker from share_info where ticker is not null """) if type(ticker) == bool and ticker == True else sa.sql.text("""select id, ticker from share_info where ticker is not null and ticker in :ticker """).bindparams(ticker=tuple(ticker))
            ).fetchall()

            # Raise a notexist exception when share couldn't be found
            if share_ids == None:
                raise NotExistException(f'Share "{" ".join(ticker)}" does not exists')
            
            # Set body params otherwise do defaults
            time_period = {'period': '1d'} if time_period == None or len(time_period) == 0 else time_period

            tickers = yf.Tickers(" ".join(list(map(lambda x: x[1], share_ids))), self.session)
            
            for tick in tickers.symbols:
                share_id = list(filter(lambda item: item[1] == tick, share_ids))[0][0]
                
                log.debug(f"fetching history of stock [{tick}] with share_id of [{share_id}]")

                tick = tickers.tickers[tick]
                res = tick.history(**time_period)

                res.rename(columns={
                    'Open': ShareHistory.open.name, 
                    'High': ShareHistory.high.name, 
                    'Low': ShareHistory.low.name, 
                    'Close': ShareHistory.close.name, 
                    'Volume': ShareHistory.volume.name, 
                    'Dividends': ShareHistory.dividends.name, 
                    'Stock Splits': ShareHistory.stock_splits.name, 
                    'Capital Gains': ShareHistory.capital_gains.name
                }, inplace=True)

                res['date'] = res.index
                res['share_id'] = share_id
                res = set_uuid(res)

                res = res.to_dict(orient='records') 

                if save and len(res) > 1:
                    stmt = pg.insert(ShareHistory).values(
                                res
                            )
                    stmt = stmt.on_conflict_do_update(
                                index_elements=['share_id', 'date'],
                                set_={
                                    ShareHistory.open.name: stmt.excluded.open,
                                    ShareHistory.close.name: stmt.excluded.close,
                                    ShareHistory.low.name: stmt.excluded.low,
                                    ShareHistory.high.name: stmt.excluded.high,
                                    ShareHistory.volume.name: stmt.excluded.volume,
                                    ShareHistory.dividends.name: stmt.excluded.dividends,
                                    ShareHistory.stock_splits.name: stmt.excluded.stock_splits,
                                    ShareHistory.capital_gains.name: stmt.excluded.capital_gains,
                                }
                            )
                    conn.execute(stmt)
                    conn.commit()

        return res 

    def get_history(self, tickers: List = None, userid: str = None):
        if userid != None:
            sel = sa.sql.text("""
select *, ROUND(CASE WHEN COALESCE(prev_price, 0) = 0 THEN 0 ELSE close / prev_price -1 END, 4) AS growth 
from (
	SELECT    
		sh.id,
		sh.share_id,
		sh.close,
		sh.date,
		si.ticker,
		Lag(sh.close) OVER (partition BY sh.share_id ORDER BY sh.date ASC) prev_price
	FROM      share_history sh
	LEFT JOIN share_info si
	ON        sh.share_id = si.id
	WHERE     
		share_id IN (
		  SELECT share_id
		  FROM   share_user
		  WHERE  user_id = :userid
		)
	AND si.ticker IS NOT NULL
	AND sh.close IS NOT NULL
) t
""")
            sel = sel.bindparams(userid=userid)

        else :
            sel = sa.sql.text("""select sh.id, sh.share_id, sh.close, sh.date, si.ticker
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
