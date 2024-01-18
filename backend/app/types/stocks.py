from typing import Annotated, List
from pydantic import BaseModel

class StockHistoryFilter(BaseModel):
    start: str
    end: Annotated[str, None] = None

class StockHistoryBody(BaseModel):
    ticker: List[str] | bool
    filter: StockHistoryFilter
    save: bool = True

class StockMatchTicker(BaseModel):
    share_id: str
    ticker: str