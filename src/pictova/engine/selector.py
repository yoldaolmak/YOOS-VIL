"""Selection helpers exposed from the canonical engine package."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.processor import get_vil_images
from src.main import load_vil_images_from_index_for_post, search_semantic_assets


def resolve_source_images(
    *,
    source: str,
    count: int | None,
    name: str | None,
    query: str | None,
    location_query: str | None,
    content_filter: str | None,
    post_context: Dict[str, Any],
) -> Dict[str, Any]:
    _count = count or 5

    if source == "auto":
        # 1. Lokal fotoğraflar (semantic search)
        files = search_semantic_assets(
            location_query=location_query or _extract_location(post_context),
            count=_count,
            content_filter=content_filter,
            post_context=post_context,
        )
        if len(files) >= _count:
            return {"source": "semantic", "query": location_query or "", "content_filter": content_filter, "files": files}

        # 2. iCloud aday fotoğraflar (UUID döner)
        icloud = search_semantic_assets(
            location_query=location_query or _extract_location(post_context),
            count=_count - len(files),
            content_filter=content_filter,
            post_context=post_context,
            include_icloud=True,
        )
        icloud_uuids = [f for f in icloud if f.startswith("icloud://")]
        if icloud_uuids:
            files = files + icloud_uuids

        return {"source": "auto", "query": location_query or "", "content_filter": content_filter, "files": files}

    if source == "semantic":
        files = search_semantic_assets(
            location_query=location_query or "",
            count=_count,
            content_filter=content_filter,
            post_context=post_context,
        )
        return {
            "source": "semantic",
            "query": location_query or "",
            "content_filter": content_filter,
            "files": files,
        }

    if source == "vil":
        files = load_vil_images_from_index_for_post(
            count=count,
            name=name,
            post_context=post_context,
        )
        if not files:
            files = get_vil_images(count=count, name=name)
        return {
            "source": "vil",
            "query": name or "",
            "content_filter": None,
            "files": files,
        }

    if source == "unsplash":
        return {
            "source": "unsplash",
            "query": query or "",
            "content_filter": None,
            "files": [],
        }

    raise ValueError(f"Unsupported source: {source}")


def _extract_location(post_context: Dict[str, Any]) -> str:
    """Post slug/title'dan konum token'ı çıkar."""
    slug = str(post_context.get("slug") or "").replace("-", " ")
    title = str(post_context.get("title") or "")
    return slug or title


__all__ = ["load_vil_images_from_index_for_post", "resolve_source_images", "search_semantic_assets"]
