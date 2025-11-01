# app/main.py

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.core.config import get_settings
from app.core.db import init_db
from contextlib import asynccontextmanager
from app.api.routes import router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code
    init_db()
    
    yield
    # shutdown code


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/", include_in_schema=False)
def redirect_to_swagger():
    return RedirectResponse("/docs")

app.include_router(router)

