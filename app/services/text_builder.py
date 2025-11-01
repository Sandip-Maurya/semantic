# app/services/text_builder.py

from typing import Sequence

def build_item_text(
    name: str | None,
    title: str | None,
    tags: Sequence[str] | None,
    description: str | None,
) -> str:
    parts: list[str] = []

    # keep the same order always
    parts.append(f"Name: {name or ''}".strip())
    parts.append(f"Title: {title or ''}".strip())

    tags_str = ", ".join(tags) if tags else ""
    parts.append(f"Tags: {tags_str}".strip())

    parts.append(f"Description: {description or ''}".strip())

    # join with \n to keep sections clear
    return "\n".join(parts)
