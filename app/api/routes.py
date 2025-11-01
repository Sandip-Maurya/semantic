# app/api/routes.py
from fastapi import APIRouter
from app.api.items import router as items_router
from app.api.search import router as search_router

router = APIRouter()


@router.get("/ping")
def ping():
    return {"message": "pong"}


router.include_router(items_router)
router.include_router(search_router)
