from typing import Annotated, List
from pydantic import BaseModel

class StockHistoryFilter(BaseModel):
    start: str
    end: Annotated[str, None] = None

class StockHistoryBody(BaseModel):
    ticker: List[str]
    filter: StockHistoryFilter
    save: bool = True
