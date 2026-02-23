"""
V2.0 内容池管理器

用途：
1) 后台刷新 RSS 内容池（可由子代理异步执行）
2) 将去重后的文章写入 shared/content_pool.json
"""

import argparse
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit, urlunsplit

from fetcher.rss import fetch_latest_article, load_feeds

ROOT_DIR = Path(__file__).resolve().parent.parent
FEEDS_FILE = ROOT_DIR / "data" / "feeds.json"
SHARED_POOL_FILE = ROOT_DIR / "shared" / "content_pool.json"
SHARED_POOL_LOG_FILE = ROOT_DIR / "shared" / "pool_log.jsonl"

POOL_MIN = 10
POOL_MAX = 20
FETCH_TIMEOUT_SECONDS = 8
CLEANUP_DAYS_DEFAULT = 7


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _append_pool_log(action: str, **fields: Any) -> None:
    record = {"action": action, "timestamp": _now_iso_utc()}
    record.update(fields)
    SHARED_POOL_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SHARED_POOL_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _parse_iso_datetime(value: Any) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except Exception:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _article_datetime(article: Dict[str, Any]) -> Optional[datetime]:
    for key in ("published_at", "fetched_at", "created_at"):
        parsed = _parse_iso_datetime(article.get(key))
        if parsed is not None:
            return parsed
    return None


def _normalize_url(url: str) -> str:
    text = (url or "").strip()
    if not text:
        return ""
    try:
        parsed = urlsplit(text)
        scheme = (parsed.scheme or "https").lower()
        netloc = parsed.netloc.lower()
        path = parsed.path or "/"
        normalized = urlunsplit((scheme, netloc, path.rstrip("/") or "/", parsed.query, ""))
        return normalized
    except Exception:
        return text


def _article_from_feed(category: str, source: Dict[str, Any], article: Dict[str, str]) -> Dict[str, Any]:
    title = str(article.get("title", "Untitled") or "Untitled").strip()
    summary = str(article.get("summary", "暂无摘要") or "暂无摘要").strip()
    url = _normalize_url(str(article.get("link", "") or ""))
    tags = [value for value in category.split("_") if value]

    return {
        "id": "{0}:{1}".format(category, source.get("name", source.get("site", "unknown"))),
        "title": title,
        "summary": summary,
        "url": url,
        "source": source.get("site", source.get("name", "unknown")),
        "tags": tags,
        "category": category,
        "fetched_at": _now_iso_utc(),
        "recommended_count": 0,
    }


def _existing_articles_for_fallback() -> List[Dict[str, Any]]:
    data = _read_json(SHARED_POOL_FILE, {})
    if not isinstance(data, dict):
        return []
    articles = data.get("articles", [])
    if not isinstance(articles, list):
        return []
    output: List[Dict[str, Any]] = []
    for item in articles:
        if not isinstance(item, dict):
            continue
        if not item.get("url"):
            continue
        output.append(item)
    return output


def refresh_pool(
    feeds_file: Path = FEEDS_FILE,
    output_file: Path = SHARED_POOL_FILE,
    pool_min: int = POOL_MIN,
    pool_max: int = POOL_MAX,
    timeout: int = FETCH_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    """
    刷新 shared 内容池。
    规则：
    - 遍历 feeds.json 的 RSS 源
    - URL 去重
    - 最多写入 pool_max 篇
    """
    feeds = load_feeds(feeds_file)
    articles: List[Dict[str, Any]] = []
    seen_urls = set()
    attempted = 0
    succeeded = 0

    for category, sources in feeds.items():
        if not isinstance(sources, list):
            continue
        for source in sources:
            if len(articles) >= pool_max:
                break
            if not isinstance(source, dict):
                continue
            feed_url = str(source.get("url", "") or "").strip()
            if not feed_url:
                continue

            attempted += 1
            try:
                latest = fetch_latest_article(feed_url, timeout=timeout)
            except Exception:
                latest = None
            if not latest:
                continue

            item = _article_from_feed(category, source, latest)
            url = item.get("url", "")
            if not url:
                continue
            if url in seen_urls:
                continue
            seen_urls.add(url)
            articles.append(item)
            succeeded += 1

        if len(articles) >= pool_max:
            break

    # 如果这次抓取不足最小阈值，用历史池子补齐（仍然 URL 去重）。
    if len(articles) < pool_min:
        for old in _existing_articles_for_fallback():
            if len(articles) >= pool_min:
                break
            url = _normalize_url(str(old.get("url", "") or ""))
            if not url or url in seen_urls:
                continue
            merged = dict(old)
            merged["url"] = url
            merged.setdefault("fetched_at", _now_iso_utc())
            merged.setdefault("recommended_count", 0)
            articles.append(merged)
            seen_urls.add(url)

    payload = {
        "articles": articles[:pool_max],
        "last_refresh": _now_iso_utc(),
        "pool_size": min(len(articles), pool_max),
        "min_threshold": 5,
        "stats": {
            "attempted_sources": attempted,
            "successful_fetches": succeeded,
            "deduped_articles": min(len(articles), pool_max),
        },
    }
    _write_json(output_file, payload)

    return payload


def cleanup_pool(
    output_file: Path = SHARED_POOL_FILE,
    days: int = CLEANUP_DAYS_DEFAULT,
) -> Dict[str, Any]:
    """
    清理超过 days 天的过期文章并写回内容池。
    """
    data = _read_json(output_file, {})
    if not isinstance(data, dict):
        data = {"articles": []}

    articles = data.get("articles", [])
    if not isinstance(articles, list):
        articles = []

    cutoff = datetime.now(timezone.utc) - timedelta(days=max(0, int(days)))
    kept: List[Dict[str, Any]] = []
    removed = 0

    for item in articles:
        if not isinstance(item, dict):
            removed += 1
            continue
        article_dt = _article_datetime(item)
        if article_dt is None:
            removed += 1
            continue
        if article_dt < cutoff:
            removed += 1
            continue
        kept.append(item)

    data["articles"] = kept
    data["pool_size"] = len(kept)
    data["last_cleanup"] = _now_iso_utc()
    data.setdefault("min_threshold", 5)
    _write_json(output_file, data)

    return {
        "articles_removed": removed,
        "pool_size": len(kept),
        "days": max(0, int(days)),
    }


def _print_refresh_summary(payload: Dict[str, Any]) -> None:
    articles = payload.get("articles", [])
    if not isinstance(articles, list):
        articles = []
    urls = [str(item.get("url", "") or "") for item in articles if isinstance(item, dict)]
    dedup_ok = len(urls) == len(set(urls))
    print("刷新完成")
    print("池子文章数: {0}".format(len(articles)))
    print("去重检查: {0}".format("True" if dedup_ok else "False"))
    if articles:
        print("样例文章: {0}".format(str(articles[0].get("title", "Untitled"))))


def _print_cleanup_summary(result: Dict[str, Any]) -> None:
    print("清理完成")
    print(
        "删除了 {0} 篇过期文章，剩余 {1} 篇".format(
            int(result.get("articles_removed", 0) or 0),
            int(result.get("pool_size", 0) or 0),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="V2 content pool manager")
    parser.add_argument("action", nargs="?", default="refresh", choices=["refresh", "cleanup"], help="pool action")
    parser.add_argument("--days", type=int, default=CLEANUP_DAYS_DEFAULT, help="cleanup threshold days, default 7")
    args = parser.parse_args()

    if args.action == "refresh":
        started_at = time.perf_counter()
        payload = refresh_pool()
        duration_sec = round(time.perf_counter() - started_at, 3)
        _print_refresh_summary(payload)
        articles = payload.get("articles", [])
        if not isinstance(articles, list):
            articles = []
        _append_pool_log(
            action="refresh",
            articles_added=len(articles),
            pool_size=int(payload.get("pool_size", 0) or 0),
            duration_sec=duration_sec,
        )
        return 0

    if args.action == "cleanup":
        started_at = time.perf_counter()
        result = cleanup_pool(days=args.days)
        duration_sec = round(time.perf_counter() - started_at, 3)
        _print_cleanup_summary(result)
        _append_pool_log(
            action="cleanup",
            articles_removed=int(result.get("articles_removed", 0) or 0),
            pool_size=int(result.get("pool_size", 0) or 0),
            duration_sec=duration_sec,
        )
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
