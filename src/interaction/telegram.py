"""Telegram interaction layer placeholder."""

from __future__ import annotations

from typing import Any


def build_brush_card(item: dict[str, Any]) -> str:
    """Build a plain-text card for a single blog item."""
    title = item.get("title", "Untitled")
    summary = item.get("summary", "No summary yet.")
    source = item.get("source", "unknown")
    tags = " ".join(f"#{tag}" for tag in item.get("tags", []))

    return (
        "📰 博客卡片\n"
        f"标题：{title}\n"
        f"摘要：{summary}\n"
        f"标签：{tags or '#general'}\n"
        f"来源：{source}"
    )
