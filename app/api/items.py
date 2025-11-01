from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from typing import List

from app.deps import DBSession
from app.models.item import Item, ItemCreate, ItemRead, ItemUpdate
from app.services.embeddings import get_embedding_for_text

router = APIRouter(prefix="/items", tags=["items"])


def build_text_for_embedding(item: ItemCreate) -> str:
    """
    Simple weighted concatenation.
    Later we can actually apply numeric weights.
    """
    parts: list[str] = []
    if item.name:
        parts.append(item.name)
    if item.tags:
        # join tags with some marker
        parts.append(" ".join(item.tags))
    if item.title:
        parts.append(item.title)
    if item.description:
        parts.append(item.description)
    return "\n".join(parts)


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, session: DBSession):
    # 1) build text
    text = build_text_for_embedding(payload)

    # 2) get embedding
    embedding = get_embedding_for_text(text)

    # 3) create item
    item = Item.model_validate(payload)
    item.embedding = embedding

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


# @router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
# def create_item(payload: ItemCreate, session: DBSession):
#     item = Item.model_validate(payload)
#     session.add(item)
#     session.commit()
#     session.refresh(item)
#     return item


@router.get("/", response_model=List[ItemRead])
def list_items(session: DBSession):
    stmt = select(Item)
    items = session.exec(stmt).all()
    return items


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, session: DBSession):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# @router.put("/{item_id}", response_model=ItemRead)
# def update_item(item_id: int, payload: ItemUpdate, session: DBSession):
#     item = session.get(Item, item_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")

#     item_data = payload.model_dump(exclude_unset=True)
#     for key, value in item_data.items():
#         setattr(item, key, value)

#     session.add(item)
#     session.commit()
#     session.refresh(item)
#     return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: DBSession):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return None


@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate, session: DBSession):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item_data = payload.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(item, key, value)

    # recalc embedding if text fields changed
    if any(k in item_data for k in ("name", "title", "description", "tags")):
        # rebuild as ItemCreate-like temp
        from app.models.item import ItemCreate
        temp = ItemCreate(
            name=item.name,
            title=item.title,
            description=item.description,
            tags=item.tags,
        )
        text = build_text_for_embedding(temp)
        item.embedding = get_embedding_for_text(text)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item
