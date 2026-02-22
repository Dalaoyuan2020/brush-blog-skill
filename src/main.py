"""
刷博客 Skill - Moltbot Skill 入口
像刷抖音一样学顶级博客，一站式知识沉淀
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fetcher.rss import fetch_latest_article, load_feeds
from interaction.telegram import build_brush_card

ROOT_DIR = Path(__file__).resolve().parent.parent
FEEDS_FILE = ROOT_DIR / "data" / "feeds.json"
PROFILES_DIR = ROOT_DIR / "data" / "profiles"


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
    # 主命令：开始刷博客
    if command == "/brush":
        feeds = load_feeds(FEEDS_FILE)
        profile = _load_profile(user_id)
        
        # M1 阶段：使用 mock 数据
        card_item = _build_mock_item(feeds)
        
        # 检查是否有真实 RSS 内容
        first_category = next(iter(feeds), "tech_programming")
        first_feed = feeds.get(first_category, [{}])[0]
        feed_url = first_feed.get("url", "")
        
        if feed_url:
            try:
                latest_article = fetch_latest_article(feed_url)
                if latest_article:
                    card_item = {
                        "title": latest_article["title"],
                        "summary": latest_article["summary"] or "暂无摘要",
                        "tags": first_category.split("_"),
                        "source": first_feed.get("site", "example.com"),
                        "link": latest_article["link"],
                    }
            except Exception:
                pass  # 使用 mock 数据
        
        message = build_brush_card(card_item)
        
        return {
            "message": message,
            "buttons": [
                [
                    {"text": "👍 感兴趣", "callback_data": "/brush like"},
                    {"text": "👎 划走", "callback_data": "/brush skip"}
                ],
                [
                    {"text": "📖 深度阅读", "callback_data": "/brush read"},
                    {"text": "💾 收藏", "callback_data": "/brush save"}
                ],
                [
                    {"text": "🔄 换一批", "callback_data": "/brush refresh"}
                ]
            ]
        }
    
    # 按钮回调处理
    elif command == "/brush like":
        # 记录正反馈
        profile = _load_profile(user_id) or {"interest_tags": {}, "read_history": []}
        # TODO: 更新兴趣分数
        _save_profile(user_id, profile)
        return {"message": "已记录，推荐相似内容 👍"}
    
    elif command == "/brush skip":
        # 记录负反馈，跳过
        return {"message": "已跳过 👎"}
    
    elif command == "/brush read":
        return {"message": "📖 深度阅读功能开发中..."}
    
    elif command == "/brush save":
        return {"message": "💾 收藏功能开发中..."}
    
    elif command == "/brush refresh":
        # 换一批：重新推荐
        return handle_command("/brush", [], user_id, context)
    
    else:
        return {"message": "未知命令，试试 /brush"}


# CLI 入口（本地测试用）
def run_brush() -> int:
    """Handle /brush command with priority RSS source and fallback."""
    feeds = load_feeds(FEEDS_FILE)
    first_category = next(iter(feeds), "tech_programming")
    first_feed = feeds.get(first_category, [{}])[0]
    card_item = _build_mock_item(feeds)

    feed_url = first_feed.get("url", "")
    if feed_url:
        try:
            latest_article = fetch_latest_article(feed_url)
        except Exception:
            latest_article = None
        if latest_article:
            card_item = {
                "title": latest_article["title"],
                "summary": latest_article["summary"] or "暂无摘要",
                "tags": first_category.split("_"),
                "source": first_feed.get("site", "example.com"),
                "link": latest_article["link"],
            }

    print(build_brush_card(card_item))
    if card_item.get("link"):
        print(f"原文：{card_item['link']}")
    print("按钮：[👍 感兴趣] [👎 划走] [📖 深度阅读] [💾 收藏] [🔄 换一批]")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Brush blog skill command runner")
    parser.add_argument("command", nargs="?", default="/brush", help="skill command, e.g. /brush")
    args = parser.parse_args()

    if args.command == "/brush":
        return run_brush()

    print(f"Unknown command: {args.command}")
    print("Try: /brush")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
