from os import getenv
from typing import List, Union

import pandas as pd
import yfinance as yf

from sqlalchemy.sql import text
import yfinance
from db_structure import get_db
from utils.yfinance_session import get_session 

from db_structure.sql_meta import StockMeta

class StockManager:
    def __init__(self, userid: str):
        self.userid = userid
        self.session = get_session()
        self.db = get_db()
        self.meta = StockMeta()        

    def getMetaData(self, list) -> yf.Tickers:
        # Get metadata
        ticks = ' '.join(list)
        tickers = yfinance.Tickers(ticks, session=self.session)

        return tickers

    def get_stocks(self, by: Union[List, str] = ['description', 'ticker']) -> pd.DataFrame:
        user_id = self.userid

        with self.db.connect() as conn:
            stm = text("""
select si.* , SUM(case when su.mutation < 0 then su.quantity else -su.quantity end) as quantity
from share_info si 
inner join share_user su on si.id = su.share_id and coalesce(si.ticker, '') <> '' and su.user_id = :user_id 
group by si.id, si.isin, si.description,si.market, si.ticker
                                """)
            
            stm = stm.bindparams(user_id=user_id)
            df = pd.read_sql(stm, con=conn)

        meta = self.getMetaData(df['ticker'].unique())
        
        df['Koers'] = df['ticker'].apply(lambda x: float(self.get_saved_quote(x)))
        
        df['totalValue'] = (df['quantity'].apply(lambda x: float(x)) * df['Koers'])
        
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

    def get_saved_quote(self, ticker: str) -> float | None:
        # We're gonna look into the database and fetch the last record
        stmt = text("""
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

    def get_history(self):
        sel = text("""
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
        sel = sel.bindparams(userid=self.userid)

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
