
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fetcher.cleaner import clean_text, summarize_text

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"


def build_structured_note(item: Dict[str, Any], user_id: str, rating: float = 5.0) -> Dict[str, Any]:
    """
    Build a structured note payload for knowledge sink.
    """
    title = clean_text(str(item.get("title", "Untitled"))) or "Untitled"
    summary = summarize_text(str(item.get("summary", "")))
    source = clean_text(str(item.get("source", "unknown"))) or "unknown"
    source_url = str(item.get("link", "") or "")
    tags = _normalize_tags(item.get("tags", []))

    return {
        "title": title,
        "source": source,
        "source_url": source_url,
        "summary": summary,
        "tags": tags,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "rating": float(rating),
        "item_key": str(item.get("item_key", "") or source_url or title),
        "user_id": user_id,
        "key_points": _build_key_points(title, summary, tags),
    }


def save_note(
    note: Dict[str, Any],
    notion_config: Optional[Dict[str, Any]] = None,
    local_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Save note into local jsonl and optionally push to Notion.
    """
    stores = []
    local_target = Path(local_path) if local_path else Path("data/saved_notes.jsonl")
    _append_local_note(local_target, note)
    stores.append("local")

    notion_config = notion_config or {}
    if not bool(notion_config.get("enabled", False)):
        return {
            "status": "saved_local",
            "stores": stores,
            "local_path": str(local_target),
        }

    api_key = str(notion_config.get("api_key", "") or "").strip()
    database_id = str(notion_config.get("database_id", "") or "").strip()
    timeout = int(notion_config.get("timeout", 10) or 10)
    if not api_key or not database_id:
        return {
            "status": "saved_local",
            "stores": stores,
            "local_path": str(local_target),
            "error": "missing_notion_credentials",
        }

    try:
        notion_result = _create_notion_page(note, api_key=api_key, database_id=database_id, timeout=timeout)
    except Exception as exc:
        return {
            "status": "saved_local_with_notion_error",
            "stores": stores,
            "local_path": str(local_target),
            "error": str(exc),
        }

    stores.append("notion")
    return {
        "status": "saved_notion",
        "stores": stores,
        "local_path": str(local_target),
        "notion_page_id": notion_result.get("id", ""),
    }


def _create_notion_page(note: Dict[str, Any], api_key: str, database_id: str, timeout: int = 10) -> Dict[str, Any]:
    payload = {
        "parent": {"database_id": database_id},
        "properties": _build_notion_properties(note),
        "children": _build_notion_children(note),
    }
    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        NOTION_API_URL,
        method="POST",
        data=data,
        headers={
            "Authorization": "Bearer {0}".format(api_key),
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError("notion_http_{0}: {1}".format(exc.code, detail))

    result = json.loads(body)
    if not isinstance(result, dict):
        raise RuntimeError("invalid_notion_response")
    return result


def _build_notion_properties(note: Dict[str, Any]) -> Dict[str, Any]:
    properties = {
        "Title": {
            "title": [{"text": {"content": str(note.get("title", "Untitled"))[:2000]}}],
        },
        "Summary": {
            "rich_text": [{"text": {"content": str(note.get("summary", "暂无摘要"))[:2000]}}],
        },
        "Tags": {
            "multi_select": [{"name": tag[:100]} for tag in note.get("tags", []) if tag],
        },
        "Saved At": {
            "date": {"start": str(note.get("saved_at", datetime.now(timezone.utc).isoformat()))},
        },
        "Rating": {
            "number": float(note.get("rating", 5.0)),
        },
    }
    source_url = str(note.get("source_url", "") or "").strip()
    if source_url:
        properties["Source"] = {"url": source_url}
    return properties


def _build_notion_children(note: Dict[str, Any]) -> List[Dict[str, Any]]:
    source = str(note.get("source", "unknown"))
    source_url = str(note.get("source_url", "") or "").strip()
    key_points = note.get("key_points", []) if isinstance(note.get("key_points", []), list) else []
    source_text = {"content": "来源：{0}".format(source)}
    if source_url:
        source_text["link"] = {"url": source_url}

    children = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": source_text,
                    }
                ]
            },
        }
    ]

    for point in key_points[:5]:
        if not point:
            continue
        children.append(
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": str(point)[:2000]}}]
                },
            }
        )

    return children


def _normalize_tags(tags: Any) -> List[str]:
    if not isinstance(tags, list):
        return []

    normalized = []
    for raw in tags:
        tag = clean_text(str(raw)).replace("#", "").strip()
        if not tag:
            continue
        normalized.append(tag[:100])
    return normalized


def _build_key_points(title: str, summary: str, tags: List[str]) -> List[str]:
    points = []
    if title:
        points.append("主题：{0}".format(title))
    if summary:
        points.append("摘要：{0}".format(summary))
    if tags:
        points.append("标签：{0}".format(", ".join(tags)))
    return points


def _append_local_note(path: Path, note: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(note, ensure_ascii=False) + "\n")
