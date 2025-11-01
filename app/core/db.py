# app/core/db.py
from sqlmodel import create_engine, Session
from app.core.config import get_settings
from typing import Generator

settings = get_settings()

# echo=True is useful in dev; you can toggle based on env
engine = create_engine(
    settings.database_url,
    # echo=(settings.app_env == "dev"),
)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency — yields a DB session and closes it after request.
    """
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """
    Import models here and create tables if needed.
    This keeps model imports local, avoiding circular imports.
    """
    from sqlmodel import SQLModel

    # later: 
    from app.models.item import Item
    SQLModel.metadata.create_all(engine)
