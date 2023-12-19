from typing import Annotated
from dotenv import load_dotenv

from fastapi import Depends, FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from utils.logger import get_logger

app = FastAPI()

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


from .dependencies import get_current_user, is_owner
from .routers import base, stocks


app.include_router(base.router)
app.include_router(stocks.router)

# app.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(get_token_header)],
#     responses={418: {"description": "I'm a teapot"}},
# )


@app.get("/")
async def splash_screen(accept: Annotated[str | None, Header()] = None):
    if 'text/html' in accept.split(','):
        # Display a simple HTML splash screen
        with open('./static/landing.html', encoding='utf-8') as f:
            fl = f.read()
        return HTMLResponse(fl)
    else:
        # Return JSON response
        return {"message": "Welcome to the splash screen!"}