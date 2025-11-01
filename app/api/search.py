# # app/api/search.py
# from typing import List, Optional

# from fastapi import APIRouter, HTTPException, status
# from sqlmodel import Session
# from sqlalchemy import text

# from app.deps import DBSession
# from app.services.embeddings import get_embedding_for_text
# from app.models.item import ItemRead

# router = APIRouter(prefix="/search", tags=["search"])


# class SearchResult(ItemRead):
#     # we’ll add a score field in response
#     score: float


# @router.post("/", response_model=List[SearchResult])
# def semantic_search(
#     query: str,
#     session: DBSession,
#     top_k: int = 5,
#     use_cosine: bool = True,
# ):
#     """
#     Perform semantic search over items table.
#     - query: natural language text
#     - top_k: how many results to return
#     - use_cosine: if True, use <#> operator, else L2 <->

#     Requires: items.embedding is a pgvector column.
#     """
#     if not query.strip():
#         raise HTTPException(status_code=400, detail="Query cannot be empty")

#     # 1) get embedding for the query
#     query_embedding = get_embedding_for_text(query)

#     # 2) build query
    
#     QUERY = text("""
#         SELECT
#             id,
#             name,
#             title,
#             description,
#             tags,
#             created_at,
#             updated_at,
#             (embedding <#> cast(:query_embedding AS vector)) AS score
#         FROM items
#         WHERE embedding IS NOT NULL
#         ORDER BY embedding <#> cast(:query_embedding AS vector)
#         LIMIT :top_k;
#     """)
    
#     rows = session.execute(QUERY, {
#         "query_embedding": query_embedding,
#         "top_k": top_k,
#     }).all()

#     results: List[SearchResult] = []
#     for row in rows:
#         # row is a RowMapping
#         result = SearchResult(
#             id=row.id,
#             name=row.name,
#             title=row.title,
#             description=row.description,
#             tags=row.tags,
#             # embedding=row.embedding,
#             created_at=row.created_at,
#             updated_at=row.updated_at,
#             score=float(row.score),
#         )
#         results.append(result)

#     return results

# app/api/search.py

# from fastapi import APIRouter, Depends, HTTPException
# from sqlmodel import Session, select
# from sqlalchemy import text
# from pydantic import BaseModel, Field
# from typing import Any

# from app.deps import DBSession
# from app.models.item import Item
# from app.services.embeddings import get_embedding_for_text
# from app.services.text_builder import build_item_text

# router = APIRouter(prefix="/search", tags=["search"])


# @router.post("/reembed", status_code=200)
# def reembed_all(session: DBSession):
#     items = session.exec(select(Item)).all()

#     if not items:
#         return {"status": "ok", "updated": 0}

#     updated = 0
#     for item in items:
#         text = build_item_text(
#             name=item.name,
#             title=item.title,
#             tags=item.tags,
#             description=item.description,
#         )
#         embedding = get_embedding_for_text(text)
#         item.embedding = embedding
#         updated += 1

#     session.commit()
#     return {"status": "ok", "updated": updated}



# class SearchRequest(BaseModel):
#     query: str = Field(default="wireless headphones with noise cancellation")
#     # allow overriding threshold per call, but optional
#     threshold: float | None = 0.30
#     # optional filter by tag
#     tag: str | None = Field(default=None, examples=[""])


# class SearchHit(BaseModel):
#     id: int
#     name: str | None = None
#     title: str | None = None
#     description: str | None = None
#     tags: list[str] | None = None
#     similarity: float


# DEFAULT_THRESHOLD = 0.30   # cosine distance (lower is better)
# DB_LIMIT = 50              # safety limit to not pull entire table
# FALLBACK_TOP_K = 2

# SEARCH_SQL = text("""
#     SELECT
#         id,
#         name,
#         title,
#         description,
#         tags,
#         created_at,
#         updated_at,
#         (embedding <=> CAST(:query_embedding AS vector)) AS score
#     FROM items
#     WHERE embedding IS NOT NULL
#     ORDER BY embedding <=> CAST(:query_embedding AS vector)
#     LIMIT :limit;
# """)


# @router.post("", response_model=list[SearchHit])
# def search_items(
#     payload: SearchRequest,
#     session: DBSession,
# ):
#     # 1. embed the query
#     query_embedding = get_embedding_for_text(payload.query)

#     # 2. run the SQL
#     params = {
#         "query_embedding": query_embedding,
#         "limit": DB_LIMIT,
        
#     }
#     rows = session.execute(
#         SEARCH_SQL,
#         params
#     ).all()

#     # 3. apply threshold in Python
#     threshold = payload.threshold or DEFAULT_THRESHOLD
#     results: list[SearchHit] = []

#     for row in rows:
#         # row is RowMapping
#         score = float(row.score)
#         if score <= threshold:
#             results.append(
#                 SearchHit(
#                     id=row.id,
#                     name=row.name,
#                     title=row.title,
#                     description=row.description,
#                     tags=row.tags,
#                     similarity=1-score,
#                 )
#             )

#     if not results:
#         for row in rows[:FALLBACK_TOP_K]:
#             score = float(row.score)
#             results.append(
#                 SearchHit(
#                     id=row.id,
#                     name=row.name,
#                     title=row.title,
#                     description=row.description,
#                     tags=row.tags,
#                     similarity=1-score,
#                 )
#             )


#     return results

from fastapi import APIRouter
from sqlmodel import Session, select
from sqlalchemy import text
from pydantic import BaseModel, Field

from app.deps import DBSession
from app.models.item import Item
from app.services.embeddings import get_embedding_for_text
from app.services.text_builder import build_item_text

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/reembed", status_code=200)
def reembed_all(session: DBSession):
    items = session.exec(select(Item)).all()

    if not items:
        return {"status": "ok", "updated": 0}

    updated = 0
    for item in items:
        text = build_item_text(
            name=item.name,
            title=item.title,
            tags=item.tags,
            description=item.description,
        )
        embedding = get_embedding_for_text(text)
        item.embedding = embedding
        updated += 1

    session.commit()
    return {"status": "ok", "updated": updated}


class SearchRequest(BaseModel):
    query: str = Field(examples=["wireless headphones with noise cancellation"])
    # similarity, not distance
    min_similarity: float | None = 0.7
    tag: str | None = None


class SearchHit(BaseModel):
    id: int
    name: str | None = None
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    similarity: float


# if similarity >= 0.7 → keep
DEFAULT_MIN_SIMILARITY = 0.70
DB_LIMIT = 50
FALLBACK_TOP_K = 2

SEARCH_SQL = text("""
    SELECT
        id,
        name,
        title,
        description,
        tags,
        created_at,
        updated_at,
        (embedding <=> CAST(:query_embedding AS vector)) AS score
    FROM items
    WHERE embedding IS NOT NULL
    AND (
    :tag = '' 
    OR :tag = ANY(COALESCE(tags, ARRAY[]::text[]))
    )    
    ORDER BY embedding <=> CAST(:query_embedding AS vector)
    LIMIT :limit;
""")


@router.post("", response_model=list[SearchHit])
def search_items(
    payload: SearchRequest,
    session: DBSession,
):
    # 1. embed query
    query_embedding = get_embedding_for_text(payload.query)

    # 2. run SQL
    tag = payload.tag or ""   # None → ""
    rows = session.execute(
        SEARCH_SQL,
        {
            "query_embedding": query_embedding,
            "tag": tag,
            "limit": DB_LIMIT,
        },
    ).all()

    min_similarity = payload.min_similarity or DEFAULT_MIN_SIMILARITY
    results: list[SearchHit] = []

    # 3. primary pass: filter on similarity
    for row in rows:
        distance = float(row.score)         # 0 = best
        similarity = 1.0 - distance         # 1 = best
        if similarity >= min_similarity:
            results.append(
                SearchHit(
                    id=row.id,
                    name=row.name,
                    title=row.title,
                    description=row.description,
                    tags=row.tags,
                    similarity=similarity,
                )
            )

    # 4. fallback: return 1–2 best anyway
    if not results:
        for row in rows[:FALLBACK_TOP_K]:
            distance = float(row.score)
            similarity = 1.0 - distance
            results.append(
                SearchHit(
                    id=row.id,
                    name=row.name,
                    title=row.title,
                    description=row.description,
                    tags=row.tags,
                    similarity=similarity,
                )
            )

    return results
