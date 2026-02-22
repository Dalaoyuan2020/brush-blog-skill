"""Entry point for brush-blog-skill M1 scaffold."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from fetcher.rss import fetch_latest_article, load_feeds
from interaction.telegram import build_brush_card

ROOT_DIR = Path(__file__).resolve().parent.parent
FEEDS_FILE = ROOT_DIR / "data" / "feeds.json"


def _build_mock_item(feeds: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
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
