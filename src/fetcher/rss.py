import json
import hashlib
import sqlite3
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

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


def init_content_db(db_path: Union[str, Path]) -> None:
    """
    Initialize content pool schema for M2.
    """
    path = str(db_path)
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS content_pool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_key TEXT NOT NULL UNIQUE,
                link TEXT,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                category TEXT,
                source TEXT,
                feed_name TEXT,
                feed_url TEXT,
                tags_json TEXT,
                fetched_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_content_pool_category ON content_pool(category)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_content_pool_fetched_at ON content_pool(fetched_at DESC)"
        )
        conn.commit()
    finally:
        conn.close()


def upsert_articles(db_path: Union[str, Path], articles: Sequence[Dict[str, Any]]) -> int:
    """
    Insert or update fetched articles into SQLite content pool.
    """
    if not articles:
        return 0

    init_content_db(db_path)
    path = str(db_path)
    fetched_at = datetime.utcnow().isoformat() + "Z"
    upserted = 0

    conn = sqlite3.connect(path)
    try:
        for article in articles:
            normalized = _normalize_article(article)
            conn.execute(
                """
                INSERT OR REPLACE INTO content_pool(
                    item_key, link, title, summary, category,
                    source, feed_name, feed_url, tags_json, fetched_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    normalized["item_key"],
                    normalized.get("link", ""),
                    normalized["title"],
                    normalized["summary"],
                    normalized.get("category", ""),
                    normalized.get("source", ""),
                    normalized.get("feed_name", ""),
                    normalized.get("feed_url", ""),
                    json.dumps(normalized.get("tags", []), ensure_ascii=False),
                    fetched_at,
                ),
            )
            upserted += 1
        conn.commit()
    finally:
        conn.close()

    return upserted


def refresh_content_pool(
    feeds: Dict[str, List[Dict[str, Any]]],
    db_path: Union[str, Path],
    priority_category: str = "priority_hn_popular_2025",
    per_category_limit: int = 1,
    max_items: int = 12,
    timeout: int = 10,
) -> int:
    """
    Fetch latest RSS items and persist them into the content pool.
    """
    articles = collect_latest_articles(
        feeds=feeds,
        priority_category=priority_category,
        per_category_limit=per_category_limit,
        max_items=max_items,
        timeout=timeout,
    )
    return upsert_articles(db_path, articles)


def pick_article_from_pool(
    db_path: Union[str, Path],
    priority_category: str = "priority_hn_popular_2025",
    exclude_item_keys: Optional[Sequence[str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Pick one article from content pool. Priority category ranks first.
    """
    candidates = list_articles_from_pool(
        db_path=db_path,
        priority_category=priority_category,
        exclude_item_keys=exclude_item_keys,
        limit=100,
    )
    if not candidates:
        return None
    return candidates[0]


def list_articles_from_pool(
    db_path: Union[str, Path],
    priority_category: str = "priority_hn_popular_2025",
    exclude_item_keys: Optional[Sequence[str]] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    List candidate articles from content pool.
    """
    init_content_db(db_path)
    path = str(db_path)
    exclude = set(exclude_item_keys or [])

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT item_key, link, title, summary, category, source, feed_name, feed_url, tags_json, fetched_at
            FROM content_pool
            ORDER BY (category = ?) DESC, fetched_at DESC
            LIMIT ?
            """,
            (priority_category, max(1, int(limit))),
        ).fetchall()
    finally:
        conn.close()

    candidates = []
    for row in rows:
        item_key = row["item_key"]
        if item_key in exclude:
            continue
        candidates.append(_row_to_article(dict(row)))
    return candidates


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


def _normalize_article(article: Dict[str, Any]) -> Dict[str, Any]:
    title = clean_text(article.get("title", "")) or "Untitled"
    summary = summarize_text(article.get("summary", ""))
    link = article.get("link", "") or ""
    source = article.get("source", "") or ""
    feed_url = article.get("feed_url", "") or ""
    feed_name = article.get("feed_name", "") or ""
    category = article.get("category", "") or ""
    tags = article.get("tags", []) or []

    item_key_base = link or "{0}|{1}|{2}".format(title, source, feed_url)
    item_key = hashlib.sha1(item_key_base.encode("utf-8")).hexdigest()

    return {
        "item_key": item_key,
        "link": link,
        "title": title,
        "summary": summary,
        "category": category,
        "source": source,
        "feed_name": feed_name,
        "feed_url": feed_url,
        "tags": tags,
    }


def _row_to_article(row: Dict[str, Any]) -> Dict[str, Any]:
    try:
        tags = json.loads(row.get("tags_json", "[]") or "[]")
        if not isinstance(tags, list):
            tags = []
    except Exception:
        tags = []

    return {
        "item_key": row.get("item_key", ""),
        "link": row.get("link", ""),
        "title": row.get("title", "Untitled"),
        "summary": row.get("summary", "暂无摘要"),
        "category": row.get("category", ""),
        "source": row.get("source", "unknown"),
        "feed_name": row.get("feed_name", ""),
        "feed_url": row.get("feed_url", ""),
        "tags": tags,
        "fetched_at": row.get("fetched_at", ""),
    }
