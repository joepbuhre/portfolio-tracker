from datetime import date,datetime, timedelta
import datetime
from decimal import Decimal
from app.types.degiro import TransactionType
from db_structure import get_db
from db_structure.model import ShareActions, User
import pandas as pd
from pydantic import BaseModel
from pyxirr import xirr
from sqlalchemy import Engine, Transaction, select, text
from stock_manager.manager import StockManager
from utils.yfinance_session import CachedLimiterSession, get_session
from utils.helpers import cross_apply

# class TestType(BaseModel):
#     userid: str
#     session: CachedLimiterSession
#     db: Engine

class StockAnalysis:
    def __init__(self, userid: str):
        self.userid = userid
        self.session = get_session()
        self.db = get_db()    

    def __total_value(self):
        sm = StockManager(self.userid)
        stocks = sm.get_stocks()
        
        return sum(stocks['totalValue'])

    def __xirr_list(self):
        with self.db.connect() as conn:
            res = conn.execute(select(ShareActions.purchase_date,ShareActions.mutation).where(
                    ShareActions.user_id == self.userid
                ).where(
                    ShareActions.action.in_(
                        (
                            TransactionType.SELL_SHARES,
                            TransactionType.BUY_SHARES,
                            TransactionType.DEGIRO_TRANSACTION_COMISSION,
                            TransactionType.DEGIRO_CONNECTIVITY_COST,
                            TransactionType.DIVIDEND,
                            TransactionType.DIVIDEND_TAX,
                        )
                    )
                )).fetchall()
            conn.close()
            return pd.DataFrame(res).to_dict(orient='records')

    def __dividend(self):
        with self.db.connect() as conn:
            res = conn.execute(select(ShareActions.mutation).where(
                    ShareActions.user_id == self.userid
                ).where(
                    ShareActions.action == TransactionType.DIVIDEND
                )).fetchall()
            
            conn.close()
        
        return sum(
            list(map(lambda x: x[0], res))
        )

    def __total_cost(self):
        with self.db.connect() as conn:
            res = conn.execute(select(ShareActions.mutation).where(
                    ShareActions.user_id == self.userid
                ).where(
                    ShareActions.action.in_(
                        (TransactionType.DEGIRO_TRANSACTION_COMISSION,
                        TransactionType.DEGIRO_CONNECTIVITY_COST)
                    )
                )).fetchall()
            
            conn.close()
        
        return sum(
            list(map(lambda x: x[0], res))
        )      


    def total_value_over_time(self):
        # https://stackoverflow.com/questions/65174354/pandas-series-groupby-and-take-cumulative-most-recent-non-null
# select 
# 	date,
# 	share_id,
                        
#     sum(total_quantity) over(partition by t.share_id order by date) * CASE WHEN coalesce(close,0) = 0 THEN lag(close) over(partition by share_id order by date) else close END 
# 		as total_value
# from (
# 	select
# 		 sh.date::date
# 		,sh.share_id
# 		,SUM(coalesce(quantity,0)) as total_quantity
# 		,sh.close as close
# 	from share_history sh
# 	left join share_actions sa on 
# 		sa.share_id = sh.share_id
# 		and sa.purchase_date::date = sh.date::date
# 		and sa.user_id = :userid
# 	group by 
# 		sh.date::date
# 		,sh.share_id
# 		,sh.close
# 	order by date
# ) t
        with self.db.connect() as conn:
            stmt = text("""
select
    sh.date::date
    ,sh.share_id
    ,SUM(coalesce(quantity,0)) as total_quantity
    ,sh.close as close
from generate_series ( '2023-01-01'::timestamp, current_timestamp, '1 day'::interval) dd
left join share_history sh on dd::date = sh.date::date
left join share_actions sa on 
    sa.share_id = sh.share_id
    and sa.purchase_date::date = sh.date::date
-- 		and sa.user_id = :userid
group by 
    sh.date::date
    ,sh.share_id
    ,sh.close
order by date
                        """).bindparams(userid=self.userid)
            
            res = conn.execute(stmt).fetchall()
            df = pd.DataFrame(res)
            df['total_quantity'] = pd.to_numeric(df['total_quantity'], errors='coerce')
            
            ## Create date lists required
            df.dropna(subset=['date'], inplace=True)
            sdate = min(df['date'])
            edate = max(df['date'])
            date_list = [sdate+timedelta(days=x) for x in range((edate-sdate).days)]
            
            ## join share_ids on date based on list
            share_ids_list = df.share_id.unique()

            df_shares = pd.merge(
                how='left',
                left=pd.DataFrame(cross_apply(date_list, share_ids_list), columns=['date', 'share_id']) ,
                right=df,
                on=['date', 'share_id']
            )
            df_shares['total_quantity'] = df_shares['total_quantity'].fillna(0)
            df_shares['ffill_close'] = df_shares.groupby('share_id')['close'].ffill().fillna(0)
            df_shares['cum_qty'] = df_shares.groupby('share_id')['total_quantity'].cumsum()

            df_shares['total_value'] = df_shares['ffill_close'].apply(Decimal) * df_shares['cum_qty'].apply(Decimal)

            return df_shares

    def __value_change(self, fromdate: date, todate: date = datetime.datetime.now().date()):
            df = self.total_value_over_time()
            first_val = df.total_value.iat[0]
            last_val = df.total_value.iat[-1]
            return last_val - first_val

    def xirr_test(self):
        # return self.__total_value()
        xirr_list = self.__xirr_list()
        total_value = self.__total_value() 
        xirr_list.append({
            'purchase_date': '2024-01-05',
            'mutation': total_value
        })
        res = xirr(
            zip(
                list(map(lambda x: datetime.datetime.strptime(x['purchase_date'], "%Y-%m-%d").date(), data)),
                list(map(lambda x: x['mutation'], data))
            )
        )

        return {
            'total_value': total_value,
            'xirr': res,
            'dividend': self.__dividend(),
            'total_cost': self.__total_cost(),
            'value_change': self.__value_change(fromdate=date(datetime.datetime.now().year, 1, 1))
        }
        

dates = [date(2020, 1, 1), date(2021, 1, 1), date(2022, 1, 1)]
amounts = [-1000, 750, 500]

data = [{"purchase_date":"2023-11-17","mutation":0.7200}, 
 {"purchase_date":"2023-11-17","mutation":-0.1100}, 
 {"purchase_date":"2023-09-28","mutation":2.1400}, 
 {"purchase_date":"2023-09-14","mutation":4.4000}, 
 {"purchase_date":"2023-09-14","mutation":-0.6600}, 
 {"purchase_date":"2023-09-13","mutation":6.2000}, 
 {"purchase_date":"2023-09-13","mutation":-0.9300}, 
 {"purchase_date":"2023-08-25","mutation":302.4000}, 
 {"purchase_date":"2023-08-25","mutation":-280.9600}, 
 {"purchase_date":"2023-08-25","mutation":-2.0000}, 
 {"purchase_date":"2023-08-25","mutation":-302.4000}, 
 {"purchase_date":"2023-08-18","mutation":0.7200}, 
 {"purchase_date":"2023-08-18","mutation":-0.1100}, 
 {"purchase_date":"2023-08-15","mutation":3.8500}, 
 {"purchase_date":"2023-08-15","mutation":-0.5800}, 
 {"purchase_date":"2023-07-20","mutation":-1.0000}, 
 {"purchase_date":"2023-07-20","mutation":-231.3600}, 
 {"purchase_date":"2023-07-20","mutation":-1.0000}, 
 {"purchase_date":"2023-07-20","mutation":-103.1400}, 
 {"purchase_date":"2023-06-29","mutation":1.3700}, 
 {"purchase_date":"2023-06-15","mutation":7.6000}, 
 {"purchase_date":"2023-06-15","mutation":-1.1400}, 
 {"purchase_date":"2023-06-02","mutation":543.0000}, 
 {"purchase_date":"2023-06-02","mutation":-505.5400}, 
 {"purchase_date":"2023-06-02","mutation":-2.0000}, 
 {"purchase_date":"2023-06-02","mutation":-543.0000}, 
 {"purchase_date":"2023-05-26","mutation":467.2000}, 
 {"purchase_date":"2023-05-26","mutation":-436.4700}, 
 {"purchase_date":"2023-05-26","mutation":-2.0000}, 
 {"purchase_date":"2023-05-26","mutation":-467.2000}, 
 {"purchase_date":"2023-05-22","mutation":322.8000}, 
 {"purchase_date":"2023-05-22","mutation":-299.2200}, 
 {"purchase_date":"2023-05-22","mutation":-2.0000}, 
 {"purchase_date":"2023-05-22","mutation":-322.8000}, 
 {"purchase_date":"2023-05-22","mutation":-344.1000}, 
 {"purchase_date":"2023-05-08","mutation":-0.6400}, 
 {"purchase_date":"2023-05-22","mutation":317.4600}, 
 {"purchase_date":"2023-05-22","mutation":-2.0000}, 
 {"purchase_date":"2023-05-22","mutation":344.1000}, 
 {"purchase_date":"2023-05-18","mutation":313.8000}, 
 {"purchase_date":"2023-05-18","mutation":-291.6300}, 
 {"purchase_date":"2023-05-18","mutation":-2.0000}, 
 {"purchase_date":"2023-05-18","mutation":-313.8000}, 
 {"purchase_date":"2023-05-17","mutation":-273.0600}, 
 {"purchase_date":"2023-05-17","mutation":251.2700}, 
 {"purchase_date":"2023-05-17","mutation":-2.0000}, 
 {"purchase_date":"2023-05-17","mutation":273.0600}, 
 {"purchase_date":"2023-05-17","mutation":270.7200}, 
 {"purchase_date":"2023-05-17","mutation":-250.6200}, 
 {"purchase_date":"2023-05-17","mutation":-2.0000}, 
 {"purchase_date":"2023-05-17","mutation":-270.7200}, 
 {"purchase_date":"2023-05-08","mutation":4.2800}, 
 {"purchase_date":"2023-05-03","mutation":0.1500}, 
 {"purchase_date":"2023-05-02","mutation":-0.1900}, 
 {"purchase_date":"2023-05-02","mutation":-4.9000}, 
 {"purchase_date":"2023-05-02","mutation":-188.0000}, 
 {"purchase_date":"2023-05-02","mutation":-3.9000}, 
 {"purchase_date":"2023-05-02","mutation":150.3200}, 
 {"purchase_date":"2023-05-02","mutation":-0.1500}, 
 {"purchase_date":"2023-05-02","mutation":-3.9000}, 
 {"purchase_date":"2023-05-02","mutation":-148.4000}, 
 {"purchase_date":"2023-04-21","mutation":-3.0000}, 
 {"purchase_date":"2023-04-21","mutation":-128.6300}, 
 {"purchase_date":"2023-04-21","mutation":-3.0000}, 
 {"purchase_date":"2023-04-21","mutation":-146.3000}, 
 {"purchase_date":"2023-04-03","mutation":-206.8200}, 
 {"purchase_date":"2023-04-03","mutation":-143.3200}, 
 {"purchase_date":"2023-03-30","mutation":0.8600}, 
 {"purchase_date":"2023-03-02","mutation":-70.9900}, 
 {"purchase_date":"2023-03-02","mutation":-210.7000}, 
 {"purchase_date":"2023-12-05","mutation":3355.33960000}]

res = xirr(
        zip(
            list(map(lambda x: datetime.datetime.strptime(x['purchase_date'], "%Y-%m-%d").date(), data)),
            list(map(lambda x: x['mutation'], data))
        )
     )