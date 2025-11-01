from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, ARRAY, JSON, String
from datetime import datetime, timezone, UTC
from pgvector.sqlalchemy import Vector

class ItemBase(SQLModel):
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    # tags: Optional[List[str]] = None
    tags: Optional[List[str]] = Field(
        default_factory=list,           
        sa_column=Column(ARRAY(String)),         
    )
    



class Item(ItemBase, table=True): 
    __tablename__ = "items" # type: ignore 

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    # pgvector column
    embedding: Optional[list[float]] = Field(
        default=None,
        sa_column=Column(Vector(1536)),
    )

class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ItemUpdate(SQLModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
