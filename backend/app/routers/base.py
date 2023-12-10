from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.dependencies import get_current_user

router = APIRouter()

@router.get("/health", response_class=PlainTextResponse)
def health(userid: Annotated[str, Depends(get_current_user)]):
    """
    Healthchecker. Just returns OK
    """
    return 'OK'

@router.get("/me")
@router.post('/login')
def read_item(user: Annotated[str, Depends(get_current_user)]):
    return user