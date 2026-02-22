
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Union, Optional, Dict, List


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
    summary = _first_text(
        item,
        ["description", "summary", "{*}summary", "content", "{*}content"],
    )
    summary = _strip_html(summary or "")

    return {
        "title": title,
        "link": link,
        "summary": summary[:200] if summary else "暂无摘要",
    }


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


def _strip_html(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
