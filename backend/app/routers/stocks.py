from typing import Annotated, Union
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
import pandas as pd

from app.dependencies import get_current_user

from stock_manager import StockManager

router = APIRouter()

@router.get('/stocks/history')
def get_history(userid: Annotated[str, Depends(get_current_user)]):
    sm = StockManager(userid)
    hist = sm.get_history()

    return hist

@router.get('/stocks/{groupby}')
def stocks_groupby(user: Annotated[str, Depends(get_current_user)], groupby: Union[str, None] = None):
    sm = StockManager(user)
    
    if groupby == None:
        groupby = ['description', 'ticker']
    else:
        groupby = groupby.split('-')
    
    df: pd.DataFrame = sm.get_stocks(groupby)
    return df.to_dict(orient='records')
