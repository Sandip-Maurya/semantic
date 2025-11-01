# app/deps.py
from typing import Annotated, Generator
from fastapi import Depends
from sqlmodel import Session


from app.core.db import get_session


def get_db_session() -> Generator[Session, None, None]:
    """
    Wrapper around core.db.get_session — in case we later add tracing/logging.
    """
    yield from get_session()


DBSession = Annotated[Session, Depends(get_db_session)]
