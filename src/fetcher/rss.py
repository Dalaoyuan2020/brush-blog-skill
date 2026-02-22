import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fetcher.cleaner import clean_text, summarize_text


def load_feeds(feeds_path: Union[str, Path]) -> Dict[str, List[Dict[str, Any]]]:
    """Load RSS feed definitions from JSON file."""
    path = Path(feeds_path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("feeds.json must contain a JSON object")

    return data


def fetch_latest_article(feed_url: str, timeout: int = 10) -> Optional[Dict[str, str]]:
    """Fetch and parse one latest article from an RSS/Atom feed URL."""
    request = urllib.request.Request(
        feed_url,
        headers={"User-Agent": "brush-blog-skill/0.1 (+https://github.com/Dalaoyuan2020/brush-blog-skill)"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read()

    root = ET.fromstring(payload)

    item = root.find(".//channel/item")
    if item is None:
        item = root.find(".//{*}entry")
    if item is None:
        return None

    title = _first_text(item, ["title", "{*}title"]) or "Untitled"
    link = _extract_link(item)
    raw_summary = _first_text(
        item,
        ["description", "summary", "{*}summary", "content", "{*}content"],
    )
    summary = summarize_text(raw_summary or "")

    return {
        "title": clean_text(title) or "Untitled",
        "link": link,
        "summary": summary,
    }


def collect_latest_articles(
    feeds: Dict[str, List[Dict[str, Any]]],
    priority_category: str = "priority_hn_popular_2025",
    per_category_limit: int = 1,
    max_items: int = 10,
    timeout: int = 10,
) -> List[Dict[str, Any]]:
    """
    Collect latest articles across feed categories.

    Priority category is processed first, then remaining categories by config order.
    """
    articles = []
    categories = _ordered_categories(feeds, priority_category)

    for category in categories:
        sources = feeds.get(category, [])
        collected_in_category = 0

        for source in sources:
            if collected_in_category >= per_category_limit:
                break
            if len(articles) >= max_items:
                return articles

            feed_url = source.get("url", "")
            if not feed_url:
                continue

            try:
                article = fetch_latest_article(feed_url, timeout=timeout)
            except Exception:
                article = None

            if not article:
                continue

            article_item = {
                "title": article.get("title", "Untitled"),
                "summary": article.get("summary", "暂无摘要"),
                "link": article.get("link", ""),
                "category": category,
                "source": source.get("site", source.get("name", "unknown")),
                "feed_name": source.get("name", ""),
                "feed_url": feed_url,
                "tags": category.split("_"),
            }
            articles.append(article_item)
            collected_in_category += 1

    return articles


def _first_text(node: ET.Element, tags: List[str]) -> Optional[str]:
    for tag in tags:
        child = node.find(tag)
        if child is not None and child.text:
            text = child.text.strip()
            if text:
                return text
    return None


def _extract_link(node: ET.Element) -> str:
    link_text = _first_text(node, ["link", "{*}link"])
    if link_text:
        return link_text

    for link_node in node.findall("link") + node.findall("{*}link"):
        href = link_node.attrib.get("href")
        if href:
            return href

    return ""


def _ordered_categories(feeds: Dict[str, List[Dict[str, Any]]], priority_category: str) -> List[str]:
    categories = list(feeds.keys())
    if priority_category in categories:
        categories.remove(priority_category)
        return [priority_category] + categories
    return categories
