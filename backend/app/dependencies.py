

from os import getenv
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app_manager import AppManager

api_key_header = APIKeyHeader(name="x-userid")

async def get_current_user(token: Annotated[str, Depends(api_key_header)]):
    """
    Get the current user if it's logged in
    """
    am = AppManager()
    res = am.login(token)

    if res == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"x-userid": "Bearer"},
        )
    return token

async def is_owner(token: Annotated[str, Depends(get_current_user)]):
    owner = token == getenv('OWNER_GUID')
    if owner == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User doesn't have permission to do this"
        )
    return owner 