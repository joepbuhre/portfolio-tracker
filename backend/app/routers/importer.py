from typing import Annotated, Union
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import HTMLResponse, PlainTextResponse
from utils.logger import log
import pandas as pd

from app.dependencies import get_current_user, is_owner
from stock_importer import StockImporter

from stock_manager import StockManager

from app.types.stocks import StockHistoryBody

router = APIRouter()

@router.post('/importer/degiro')
def post_importer_degiro(file: UploadFile, userid: Annotated[str, Depends(get_current_user)]):
    log.debug('Importing file')
    
    imp = StockImporter(userid)
    imp.add_shares(file.file)

    return True