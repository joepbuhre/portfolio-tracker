from typing import Annotated
from pydantic import BaseModel

class StockHistoryFilter(BaseModel):
    start: str
    end: Annotated[str, None] = None

class StockHistoryBody(BaseModel):
    ticker: str
    filter: StockHistoryFilter
    save: bool = True
