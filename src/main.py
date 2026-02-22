"""
刷博客 Skill - Moltbot Skill 入口
像刷抖音一样学顶级博客，一站式知识沉淀
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fetcher.rss import (
    collect_latest_articles,
    load_feeds,
    pick_article_from_pool,
    refresh_content_pool,
)
from interaction.telegram import (
    build_brush_buttons,
    build_brush_card,
    build_deep_read_message,
    build_saved_message,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
FEEDS_FILE = ROOT_DIR / "data" / "feeds.json"
CONTENT_DB = ROOT_DIR / "data" / "content.db"
PROFILES_DIR = ROOT_DIR / "data" / "profiles"
READ_HISTORY_LIMIT = 100
SAVED_ITEMS_LIMIT = 200


def _build_mock_item(feeds: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Create one fake card item based on configured feeds."""
    first_category = next(iter(feeds), "tech_programming")
    first_feed = feeds.get(first_category, [{}])[0]

    return {
        "title": f"今日推荐：{first_feed.get('name', 'Top Blog')}",
        "summary": "这是 M1 阶段的假数据卡片，用于打通 /brush 命令链路。",
        "tags": first_category.split("_"),
        "source": first_feed.get("site", "example.com"),
        "link": "",
    }


def _build_recommended_item(
    feeds: Dict[str, List[Dict[str, Any]]], history_item_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Build one recommended card item from content pool with live fallback.
    """
    card_item = _build_mock_item(feeds)
    exclude_keys = history_item_keys or []

    try:
        refresh_content_pool(
            feeds,
            db_path=CONTENT_DB,
            priority_category="priority_hn_popular_2025",
            per_category_limit=1,
            max_items=12,
            timeout=10,
        )
    except Exception:
        pass

    try:
        pooled_article = pick_article_from_pool(
            CONTENT_DB,
            priority_category="priority_hn_popular_2025",
            exclude_item_keys=exclude_keys,
        )
    except Exception:
        pooled_article = None

    if pooled_article:
        card_item.update(
            {
                "title": pooled_article.get("title", card_item["title"]),
                "summary": pooled_article.get("summary", card_item["summary"]),
                "tags": pooled_article.get("tags", card_item["tags"]),
                "source": pooled_article.get("source", card_item["source"]),
                "link": pooled_article.get("link", ""),
                "item_key": pooled_article.get("item_key", ""),
            }
        )
        return card_item

    try:
        articles = collect_latest_articles(
            feeds,
            priority_category="priority_hn_popular_2025",
            per_category_limit=1,
            max_items=1,
            timeout=10,
        )
    except Exception:
        articles = []

    if not articles:
        return card_item

    top_article = articles[0]
    card_item.update(
        {
            "title": top_article.get("title", card_item["title"]),
            "summary": top_article.get("summary", card_item["summary"]),
            "tags": top_article.get("tags", card_item["tags"]),
            "source": top_article.get("source", card_item["source"]),
            "link": top_article.get("link", ""),
            "item_key": "",
        }
    )
    return card_item


def _load_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Load user profile if exists."""
    profile_path = PROFILES_DIR / f"{user_id}.json"
    if profile_path.exists():
        with profile_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _save_profile(user_id: str, profile: Dict[str, Any]) -> None:
    """Save user profile."""
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    profile_path = PROFILES_DIR / f"{user_id}.json"
    with profile_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def _default_profile() -> Dict[str, Any]:
    return {
        "interest_tags": {},
        "read_history": [],
        "saved_items": [],
        "last_item": {},
    }


def _record_read_history(profile: Dict[str, Any], item_key: str) -> Dict[str, Any]:
    """Append one item key into read history with cap and de-duplication."""
    history = profile.get("read_history", [])
    if not isinstance(history, list):
        history = []

    if item_key:
        history = [value for value in history if value != item_key]
        history.append(item_key)
        history = history[-READ_HISTORY_LIMIT:]

    profile["read_history"] = history
    return profile


def _record_saved_item(profile: Dict[str, Any], item: Dict[str, Any]) -> Dict[str, Any]:
    saved_items = profile.get("saved_items", [])
    if not isinstance(saved_items, list):
        saved_items = []

    item_key = item.get("item_key", "")
    normalized_item = {
        "item_key": item_key,
        "title": item.get("title", "Untitled"),
        "source": item.get("source", "unknown"),
        "link": item.get("link", ""),
        "summary": item.get("summary", "暂无摘要"),
    }

    if item_key:
        saved_items = [entry for entry in saved_items if entry.get("item_key", "") != item_key]
    saved_items.append(normalized_item)
    saved_items = saved_items[-SAVED_ITEMS_LIMIT:]
    profile["saved_items"] = saved_items
    return profile


def _update_interest_tags(profile: Dict[str, Any], tags: List[str], delta: int) -> Dict[str, Any]:
    interest = profile.get("interest_tags", {})
    if not isinstance(interest, dict):
        interest = {}

    for tag in tags:
        if not tag:
            continue
        old_value = float(interest.get(tag, 0.0))
        interest[tag] = round(old_value + float(delta), 2)

    profile["interest_tags"] = interest
    return profile


def _build_card_message(item: Dict[str, Any]) -> str:
    message = build_brush_card(item)
    if item.get("link"):
        message += "\n原文：{0}".format(item["link"])
    return message


def _build_brush_response(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "message": _build_card_message(item),
        "buttons": build_brush_buttons(),
    }


def _next_item_response(user_id: str, profile: Dict[str, Any], feeds: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    history = profile.get("read_history", [])
    if not isinstance(history, list):
        history = []

    card_item = _build_recommended_item(feeds, history_item_keys=history)
    profile["last_item"] = card_item
    profile = _record_read_history(profile, card_item.get("item_key", ""))
    _save_profile(user_id, profile)

    return _build_brush_response(card_item)


def _merge_command_and_args(command: str, args: List[str]) -> str:
    if args and command.startswith("/"):
        return "{0} {1}".format(command, " ".join(args))
    return command


def handle_command(command: str, args: List[str], user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理用户命令
    
    Args:
        command: 命令字符串（如 "/brush"）
        args: 命令参数列表
        user_id: 用户 ID
        context: 上下文（包含用户配置、数据等）
    
    Returns:
        dict: {
            "message": str,           # 回复消息
            "buttons": [[{"text": str, "callback_data": str}]],  # 按钮（可选）
        }
    """
    command = _merge_command_and_args(command, args)
    profile = _load_profile(user_id) or _default_profile()

    # 主命令：开始刷博客
    if command == "/brush":
        feeds = load_feeds(FEEDS_FILE)
        return _next_item_response(user_id, profile, feeds)
    
    # 按钮回调处理
    elif command == "/brush like":
        last_item = profile.get("last_item", {}) if isinstance(profile.get("last_item", {}), dict) else {}
        tags = last_item.get("tags", []) if isinstance(last_item.get("tags", []), list) else []
        profile = _update_interest_tags(profile, tags, delta=2)
        _save_profile(user_id, profile)
        feeds = load_feeds(FEEDS_FILE)
        response = _next_item_response(user_id, profile, feeds)
        response["message"] = "✅ 已记录偏好（+2）\n\n" + response["message"]
        return response
    
    elif command == "/brush skip":
        last_item = profile.get("last_item", {}) if isinstance(profile.get("last_item", {}), dict) else {}
        tags = last_item.get("tags", []) if isinstance(last_item.get("tags", []), list) else []
        profile = _update_interest_tags(profile, tags, delta=-1)
        _save_profile(user_id, profile)
        feeds = load_feeds(FEEDS_FILE)
        response = _next_item_response(user_id, profile, feeds)
        response["message"] = "⏭️ 已跳过（-1）\n\n" + response["message"]
        return response
    
    elif command == "/brush read":
        last_item = profile.get("last_item", {}) if isinstance(profile.get("last_item", {}), dict) else {}
        if not last_item:
            return {"message": "还没有可展开的文章，先试试 /brush", "buttons": build_brush_buttons()}
        return {"message": build_deep_read_message(last_item), "buttons": build_brush_buttons()}
    
    elif command == "/brush save":
        last_item = profile.get("last_item", {}) if isinstance(profile.get("last_item", {}), dict) else {}
        if not last_item:
            return {"message": "还没有可收藏的文章，先试试 /brush", "buttons": build_brush_buttons()}
        profile = _record_saved_item(profile, last_item)
        profile = _update_interest_tags(
            profile,
            last_item.get("tags", []) if isinstance(last_item.get("tags", []), list) else [],
            delta=5,
        )
        _save_profile(user_id, profile)
        return {"message": build_saved_message(last_item), "buttons": build_brush_buttons()}
    
    elif command == "/brush refresh":
        feeds = load_feeds(FEEDS_FILE)
        response = _next_item_response(user_id, profile, feeds)
        response["message"] = "🔄 已换一批\n\n" + response["message"]
        return response
    
    else:
        return {"message": "未知命令，试试 /brush"}


# CLI 入口（本地测试用）
def run_brush() -> int:
    """Handle /brush command with priority RSS source and fallback."""
    feeds = load_feeds(FEEDS_FILE)
    card_item = _build_recommended_item(feeds)

    print(build_brush_card(card_item))
    if card_item.get("link"):
        print(f"原文：{card_item['link']}")
    print("按钮：[👍 感兴趣] [👎 划走] [📖 深度阅读] [💾 收藏] [🔄 换一批]")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Brush blog skill command runner")
    parser.add_argument("command", nargs="?", default="/brush", help="skill command, e.g. /brush")
    parser.add_argument("args", nargs="*", help="command args")
    args = parser.parse_args()

    if args.command == "/brush" and not args.args:
        return run_brush()

    result = handle_command(args.command, args.args, "cli-user", {})
    print(result.get("message", ""))
    buttons = result.get("buttons", [])
    if buttons:
        button_texts = []
        for row in buttons:
            row_labels = " ".join("[{0}]".format(btn.get("text", "")) for btn in row)
            button_texts.append(row_labels)
        print("按钮：" + " | ".join(button_texts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
