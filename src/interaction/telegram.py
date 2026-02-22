
from typing import Any, Union, Optional, Dict, List


def build_brush_card(item: Dict[str, Any]) -> str:
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


def build_brush_buttons() -> List[List[Dict[str, str]]]:
    """Return standard brush interaction buttons."""
    return [
        [
            {"text": "👍 感兴趣", "callback_data": "/brush like"},
            {"text": "👎 划走", "callback_data": "/brush skip"},
        ],
        [
            {"text": "📖 深度阅读", "callback_data": "/brush read"},
            {"text": "💾 收藏", "callback_data": "/brush save"},
        ],
        [
            {"text": "🔄 换一批", "callback_data": "/brush refresh"},
        ],
    ]


def build_cold_start_buttons() -> List[List[Dict[str, str]]]:
    """Return buttons used in cold-start onboarding flow."""
    return [
        [
            {"text": "👍 这个领域感兴趣", "callback_data": "/brush like"},
            {"text": "👎 下一个领域", "callback_data": "/brush skip"},
        ],
        [
            {"text": "📖 先读这篇", "callback_data": "/brush read"},
            {"text": "🔄 换个领域", "callback_data": "/brush refresh"},
        ],
    ]


def build_deep_read_message(item: Dict[str, Any]) -> str:
    """Build expanded reading text for last recommended article."""
    title = item.get("title", "Untitled")
    summary = item.get("summary", "暂无摘要")
    source = item.get("source", "unknown")
    link = item.get("link", "")

    message = (
        "📖 深度阅读\n"
        f"标题：{title}\n"
        f"来源：{source}\n\n"
        f"{summary}"
    )
    if link:
        message += "\n\n原文：{0}".format(link)
    return message


def build_saved_message(item: Dict[str, Any]) -> str:
    """Build acknowledge message for save action."""
    title = item.get("title", "Untitled")
    return "✅ 已收藏：{0}".format(title)
