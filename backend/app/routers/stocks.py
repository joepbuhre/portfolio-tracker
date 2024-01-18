from time import sleep
from typing import Annotated, List, Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
import pandas as pd

from app.dependencies import get_current_user, is_owner
from stock_importer import StockImporter

from stock_manager import StockManager

from app.types.stocks import StockHistoryBody, StockMatchTicker
from stock_manager.analysis import StockAnalysis

router = APIRouter()

@router.get('/stocks')
def get_all_stocks(userid: Annotated[str, Depends(get_current_user)]):
    sm = StockManager(userid)
    return sm.get_stocks().to_dict(orient='records')

@router.get('/stocks/total-value')
def stocks_get_total_value(userid: Annotated[str, Depends(get_current_user)]):
    sa = StockAnalysis(userid)
    return sa.total_value_over_time().groupby('date')['total_value'].sum().reset_index().to_dict(orient='records')

@router.get('/stocks/dashboard-stats')
def stocks_dashboard_stats(userid: Annotated[str, Depends(get_current_user)]):
    sm = StockAnalysis(userid)
    return sm.xirr_test()
    

@router.get('/stocks/match-tickers')
def get_all_stocks(user_id: Annotated[str, Depends(get_current_user)], is_owner: Annotated[str, Depends(is_owner)]):
    sm = StockManager(user_id)
    return sm.get_raw_stocks().to_dict(orient='records')

@router.post('/stocks/match-tickers')
def get_all_stocks(post_object: List[StockMatchTicker] ,user_id: Annotated[str, Depends(get_current_user)], is_owner: Annotated[str, Depends(is_owner)]):
    sm = StockManager(user_id)
    return sm.match_ticker(post_object)

@router.get('/stocks/history')
def get_history(userid: Annotated[str, Depends(get_current_user)]):
    sm = StockManager(userid)
    hist = sm.get_history()
    return hist


@router.post('/stocks/set-stock-history')
def stocks_set_stock_history(body: StockHistoryBody,isowner: Annotated[bool, Depends(is_owner)]):
    return StockImporter('').set_history(ticker=body.ticker, time_period=dict(body.filter), save=body.save)

@router.get('/stocks/statistics')
def stocks_statistics(user: Annotated[str, Depends(get_current_user)]):
    sm = StockManager(user)

from stock_manager.degiro import DeGiro
@router.get('/stocks/actions')
def stocks_actions(user: Annotated[str, Depends(get_current_user)]):
    dg = DeGiro()
    return dg.get_account()

@router.get('/stocks/{groupby}')
def stocks_groupby(user: Annotated[str, Depends(get_current_user)], groupby: Union[str, None] = None):
    sm = StockManager(user)
    
    if groupby == None:
        groupby = ['description', 'ticker']
    else:
        groupby = groupby.split('-')
    
    df: pd.DataFrame = sm.get_stocks(groupby)
    return df.to_dict(orient='records')