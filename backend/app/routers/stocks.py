from typing import Annotated, Union
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
import pandas as pd

from app.dependencies import get_current_user, is_owner
from stock_importer import StockImporter

from stock_manager import StockManager
from tomlkit import boolean

from app.types.stocks import StockHistoryBody

router = APIRouter()

@router.get('/stocks')
def get_all_stocks(userid: Annotated[str, Depends(get_current_user)]):
    sm = StockManager(userid)
    return sm.get_stocks().to_dict(orient='records')

@router.get('/stocks/history')
def get_history(userid: Annotated[str, Depends(get_current_user)]):
    sm = StockManager(userid)
    hist = sm.get_history()

    return hist


@router.post('/stocks/set-stock-history')
def stocks_set_stock_history(body: StockHistoryBody,isowner: Annotated[bool, Depends(is_owner)]):
    return StockImporter().set_history(ticker=body.ticker, filter=dict(body.filter), save=body.save)

@router.get('/stocks/{groupby}')
def stocks_groupby(user: Annotated[str, Depends(get_current_user)], groupby: Union[str, None] = None):
    sm = StockManager(user)
    
    if groupby == None:
        groupby = ['description', 'ticker']
    else:
        groupby = groupby.split('-')
    
    df: pd.DataFrame = sm.get_stocks(groupby)
    return df.to_dict(orient='records')

@router.get('/stocks/statistics')
def stocks_statistics(user: Annotated[str, Depends(get_current_user)]):
    sm = StockManager(user)

