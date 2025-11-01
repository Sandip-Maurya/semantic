# app/services/embeddings.py
from typing import List
from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def get_embedding_for_text(text: str) -> List[float]:
    """
    Generate an embedding vector for a given text.
    """
    client = get_client()
    resp = client.embeddings.create(
        model=settings.openai_embed_model,
        input=text,
    )
    # OpenAI returns: data[0].embedding
    return resp.data[0].embedding
