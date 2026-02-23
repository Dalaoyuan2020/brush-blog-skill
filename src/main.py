"""
刷博客 Skill - Moltbot Skill 入口
像刷抖音一样学顶级博客，一站式知识沉淀
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fetcher.rss import (
    collect_latest_articles,
    get_content_pool_stats,
    list_articles_by_category,
    list_articles_from_pool,
    load_feeds,
    refresh_content_pool,
)
from fetcher.reader import (
    build_deep_read_snippet,
    build_plain_language_explanation,
    fetch_full_article_text,
)
from fetcher.cleaner import summarize_text
from interaction.telegram import (
    build_brush_buttons,
    build_brush_card,
    build_cold_start_buttons,
    build_deep_read_message,
    build_saved_message,
)
from recommend.scorer import rank_items
from sink.notion import build_structured_note, save_note
from tracker.behavior import log_behavior_event

ROOT_DIR = Path(__file__).resolve().parent.parent
FEEDS_FILE = ROOT_DIR / "data" / "feeds.json"
CONTENT_DB = ROOT_DIR / "data" / "content.db"
PROFILES_DIR = ROOT_DIR / "data" / "profiles"
BEHAVIOR_EVENTS_FILE = ROOT_DIR / "data" / "behavior_events.jsonl"
SAVED_NOTES_FILE = ROOT_DIR / "data" / "saved_notes.jsonl"
READ_HISTORY_LIMIT = 100
SAVED_ITEMS_LIMIT = 200
SOURCE_HISTORY_LIMIT = 50
COLD_START_MIN_SELECTIONS = 2
COLD_START_MAX_SELECTIONS = 3
COLD_START_MAX_CATEGORIES = 6
QUICK_LEARN_REBALANCE_INTERVAL = 5
BASE_RECOMMEND_WEIGHTS = {
    "interest": 0.4,
    "knowledge": 0.3,
    "diversity": 0.2,
    "popularity": 0.1,
}
COLD_START_CATEGORY_ORDER = [
    "tech_programming",
    "ai_ml",
    "business_startup",
    "design_product",
    "science_general",
    "priority_hn_popular_2025",
]
COLD_START_CATEGORY_LABELS = {
    "tech_programming": "技术/编程",
    "ai_ml": "AI/ML",
    "business_startup": "商业/创业",
    "design_product": "设计/产品",
    "science_general": "科学/通识",
    "priority_hn_popular_2025": "热门精选",
}
COLD_START_CATEGORY_ALIASES = {
    "tech_programming": "tech",
    "ai_ml": "ai",
    "business_startup": "biz",
    "design_product": "design",
    "science_general": "science",
    "priority_hn_popular_2025": "popular",
}
COLD_START_CATEGORY_TAG_HINTS = {
    "tech_programming": ["tech", "programming", "engineering", "backend"],
    "ai_ml": ["ai", "ml", "llm", "agent"],
    "business_startup": ["business", "startup", "growth", "product"],
    "design_product": ["design", "ux", "ui", "product"],
    "science_general": ["science", "research", "biology", "physics"],
    "priority_hn_popular_2025": ["hn", "popular", "trend", "tech"],
}
COLD_START_ALIAS_TO_CATEGORY = {
    alias: category for category, alias in COLD_START_CATEGORY_ALIASES.items()
}


def _env_int(name: str, default: int, min_value: int = 1) -> int:
    raw = os.getenv(name, "")
    if not raw:
        return default
    try:
        value = int(raw)
    except Exception:
        return default
    if value < min_value:
        return min_value
    return value


def _env_float(name: str, default: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    raw = os.getenv(name, "")
    if not raw:
        return default
    try:
        value = float(raw)
    except Exception:
        return default
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


POOL_MIN_ITEMS = _env_int("BRUSH_POOL_MIN_ITEMS", 4)
POOL_REFRESH_MIN_INTERVAL_SECONDS = _env_int("BRUSH_POOL_REFRESH_INTERVAL_SEC", 20 * 60)
POOL_REFRESH_TIMEOUT_SECONDS = _env_int("BRUSH_POOL_REFRESH_TIMEOUT_SEC", 4)
POOL_REFRESH_MAX_ITEMS = _env_int("BRUSH_POOL_REFRESH_MAX_ITEMS", 4)
POOL_REFRESH_PER_CATEGORY_LIMIT = _env_int("BRUSH_POOL_REFRESH_PER_CATEGORY", 1)
FALLBACK_FETCH_TIMEOUT_SECONDS = _env_int("BRUSH_FALLBACK_FETCH_TIMEOUT_SEC", 4)
DEEP_READ_FETCH_TIMEOUT_SECONDS = _env_int("BRUSH_DEEP_READ_TIMEOUT_SEC", 6)
QUICK_LEARN_INTERACTIONS = _env_int("BRUSH_QUICK_LEARN_INTERACTIONS", 20)
QUICK_LEARN_DIVERSITY_WEIGHT = _env_float("BRUSH_QUICK_LEARN_DIVERSITY_WEIGHT", 0.4)
_FEEDS_CACHE: Dict[str, Any] = {"mtime": None, "data": None}


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


def _load_feeds_cached() -> Dict[str, List[Dict[str, Any]]]:
    """
    Read feeds config with mtime cache to avoid repetitive JSON parsing.
    """
    try:
        mtime = FEEDS_FILE.stat().st_mtime
    except Exception:
        mtime = None

    if _FEEDS_CACHE.get("data") is not None and _FEEDS_CACHE.get("mtime") == mtime:
        return _FEEDS_CACHE["data"]

    feeds = load_feeds(FEEDS_FILE)
    _FEEDS_CACHE["mtime"] = mtime
    _FEEDS_CACHE["data"] = feeds
    return feeds


def _should_refresh_content_pool() -> bool:
    """
    Decide whether to refresh RSS pool based on age and item count.
    """
    try:
        stats = get_content_pool_stats(CONTENT_DB)
    except Exception:
        return True

    total = int(stats.get("total_count", 0) or 0)
    age_seconds = stats.get("age_seconds")
    if total < POOL_MIN_ITEMS:
        return True
    if age_seconds is None:
        return True
    return int(age_seconds) >= POOL_REFRESH_MIN_INTERVAL_SECONDS


def _maybe_refresh_content_pool(feeds: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    Lightweight refresh: only refresh when pool is stale or too small.
    """
    if not _should_refresh_content_pool():
        return

    try:
        refresh_content_pool(
            feeds,
            db_path=CONTENT_DB,
            priority_category="priority_hn_popular_2025",
            per_category_limit=POOL_REFRESH_PER_CATEGORY_LIMIT,
            max_items=POOL_REFRESH_MAX_ITEMS,
            timeout=POOL_REFRESH_TIMEOUT_SECONDS,
        )
    except Exception:
        return


def _build_recommended_item(
    feeds: Dict[str, List[Dict[str, Any]]],
    profile: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Build one recommended card item from content pool with live fallback.
    """
    card_item = _build_mock_item(feeds)
    history_item_keys = profile.get("read_history", [])
    if not isinstance(history_item_keys, list):
        history_item_keys = []
    exclude_keys = history_item_keys

    _maybe_refresh_content_pool(feeds)

    try:
        candidates = list_articles_from_pool(
            CONTENT_DB,
            priority_category="priority_hn_popular_2025",
            exclude_item_keys=exclude_keys,
            limit=50,
        )
        if candidates:
            ranked = rank_items(
                candidates,
                profile=profile,
                recent_sources=profile.get("source_history", [])
                if isinstance(profile.get("source_history", []), list)
                else [],
                weights=weights or BASE_RECOMMEND_WEIGHTS,
            )
            pooled_article = ranked[0]
        else:
            pooled_article = None
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
            timeout=FALLBACK_FETCH_TIMEOUT_SECONDS,
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
        "source_history": [],
        "saved_items": [],
        "last_item": {},
        "learning": {
            "phase": "cold_start",
            "interaction_count": 0,
            "quick_limit": QUICK_LEARN_INTERACTIONS,
            "last_rebalanced_at": 0,
        },
        "cold_start": {
            "active": True,
            "completed": False,
            "seed_items": [],
            "current_index": 0,
            "selected_categories": [],
            "seen_categories": [],
        },
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


def _record_source_history(profile: Dict[str, Any], source: str) -> Dict[str, Any]:
    history = profile.get("source_history", [])
    if not isinstance(history, list):
        history = []

    if source:
        history.append(source)
        history = history[-SOURCE_HISTORY_LIMIT:]
    profile["source_history"] = history
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


def _recalibrate_interest_tags(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Light rebalance for quick-learning phase:
    keep strong tags and suppress noisy weak signals.
    """
    interest = profile.get("interest_tags", {})
    if not isinstance(interest, dict) or not interest:
        return profile

    rebalanced: Dict[str, float] = {}
    for tag, value in interest.items():
        try:
            numeric = float(value)
        except Exception:
            continue
        adjusted = round(numeric * 0.95, 3)
        if adjusted >= 0.15 or adjusted <= -0.15:
            rebalanced[tag] = adjusted

    profile["interest_tags"] = rebalanced
    return profile


def _ensure_learning_state(profile: Dict[str, Any]) -> Dict[str, Any]:
    state = profile.get("learning", {})
    if not isinstance(state, dict):
        state = {}

    phase = state.get("phase", "")
    interaction_count = state.get("interaction_count", 0)
    quick_limit = state.get("quick_limit", QUICK_LEARN_INTERACTIONS)
    last_rebalanced_at = state.get("last_rebalanced_at", 0)

    try:
        interaction_count = max(0, int(interaction_count))
    except Exception:
        interaction_count = 0
    try:
        quick_limit = max(1, int(quick_limit))
    except Exception:
        quick_limit = QUICK_LEARN_INTERACTIONS
    try:
        last_rebalanced_at = max(0, int(last_rebalanced_at))
    except Exception:
        last_rebalanced_at = 0

    if phase not in ("cold_start", "quick", "stable"):
        cold_state = _ensure_cold_start_state(profile)
        if bool(cold_state.get("active", False)) and not bool(cold_state.get("completed", False)):
            phase = "cold_start"
        else:
            # Keep existing users in stable mode by default to avoid changing their experience.
            phase = "stable"

    normalized = {
        "phase": phase,
        "interaction_count": interaction_count,
        "quick_limit": quick_limit,
        "last_rebalanced_at": last_rebalanced_at,
    }
    profile["learning"] = normalized
    return normalized


def _activate_quick_learning(profile: Dict[str, Any]) -> Dict[str, Any]:
    state = _ensure_learning_state(profile)
    state["phase"] = "quick"
    state["interaction_count"] = 0
    state["quick_limit"] = QUICK_LEARN_INTERACTIONS
    state["last_rebalanced_at"] = 0
    profile["learning"] = state
    return state


def _category_interest_tags(category: str) -> List[str]:
    tags = []
    for tag in category.split("_"):
        if tag and tag not in tags:
            tags.append(tag)
    alias = COLD_START_CATEGORY_ALIASES.get(category, "")
    if alias and alias not in tags:
        tags.append(alias)
    for tag in COLD_START_CATEGORY_TAG_HINTS.get(category, []):
        if tag and tag not in tags:
            tags.append(tag)
    return tags


def _resolve_recommend_weights(profile: Dict[str, Any]) -> Dict[str, float]:
    learning = _ensure_learning_state(profile)
    if learning.get("phase") != "quick":
        return dict(BASE_RECOMMEND_WEIGHTS)

    diversity = QUICK_LEARN_DIVERSITY_WEIGHT
    remaining = max(0.0, 1.0 - diversity)
    ratio_total = BASE_RECOMMEND_WEIGHTS["interest"] + BASE_RECOMMEND_WEIGHTS["knowledge"] + BASE_RECOMMEND_WEIGHTS["popularity"]
    if ratio_total <= 0:
        return dict(BASE_RECOMMEND_WEIGHTS)

    interest = round(remaining * (BASE_RECOMMEND_WEIGHTS["interest"] / ratio_total), 4)
    knowledge = round(remaining * (BASE_RECOMMEND_WEIGHTS["knowledge"] / ratio_total), 4)
    popularity = round(max(0.0, 1.0 - diversity - interest - knowledge), 4)
    return {
        "interest": interest,
        "knowledge": knowledge,
        "diversity": round(diversity, 4),
        "popularity": popularity,
    }


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


def _ensure_cold_start_state(profile: Dict[str, Any]) -> Dict[str, Any]:
    state = profile.get("cold_start")
    if "cold_start" in profile and isinstance(state, dict):
        completed = bool(state.get("completed", False))
        active = bool(state.get("active", not completed))
        seed_items = state.get("seed_items", [])
        current_index = state.get("current_index", 0)
        selected_categories = state.get("selected_categories", [])
        seen_categories = state.get("seen_categories", [])
    else:
        has_history = bool(profile.get("read_history")) or bool(profile.get("interest_tags"))
        completed = has_history
        active = not completed
        seed_items = []
        current_index = 0
        selected_categories = []
        seen_categories = []

    if not isinstance(seed_items, list):
        seed_items = []
    if not isinstance(selected_categories, list):
        selected_categories = []
    if not isinstance(seen_categories, list):
        seen_categories = []
    normalized_selected: List[str] = []
    for category in selected_categories:
        if not isinstance(category, str):
            continue
        category = category.strip()
        if category in COLD_START_CATEGORY_ALIASES and category not in normalized_selected:
            normalized_selected.append(category)
    selected_categories = normalized_selected[:COLD_START_MAX_SELECTIONS]

    try:
        current_index = int(current_index)
    except Exception:
        current_index = 0
    if current_index < 0:
        current_index = 0

    normalized = {
        "active": active,
        "completed": completed,
        "seed_items": seed_items,
        "current_index": current_index,
        "selected_categories": selected_categories,
        "seen_categories": seen_categories,
    }
    profile["cold_start"] = normalized
    return normalized


def _is_cold_start_active(profile: Dict[str, Any]) -> bool:
    state = _ensure_cold_start_state(profile)
    return bool(state.get("active", False)) and not bool(state.get("completed", False))


def _pick_cold_start_categories(feeds: Dict[str, List[Dict[str, Any]]]) -> List[str]:
    categories = []
    for category in COLD_START_CATEGORY_ORDER:
        if category in feeds and category not in categories:
            categories.append(category)
    if len(categories) >= COLD_START_MAX_CATEGORIES:
        return categories[:COLD_START_MAX_CATEGORIES]

    for category in feeds.keys():
        if category in categories:
            continue
        categories.append(category)
        if len(categories) >= COLD_START_MAX_CATEGORIES:
            break
    return categories


def _build_seed_item(feeds: Dict[str, List[Dict[str, Any]]], category: str) -> Dict[str, Any]:
    article = None
    try:
        pooled = list_articles_by_category(CONTENT_DB, category=category, limit=1)
    except Exception:
        pooled = []
    if pooled:
        article = pooled[0]

    feed_source = feeds.get(category, [{}])[0] if feeds.get(category) else {}
    if not article:
        source_name = feed_source.get("site", feed_source.get("name", "unknown"))
        seed = {
            "title": "领域种子：{0}".format(feed_source.get("name", category)),
            "summary": "先告诉我你对这个领域是否感兴趣，我会据此调整推荐方向。",
            "tags": category.split("_"),
            "source": source_name,
            "link": "",
            "item_key": "",
            "category": category,
            "cold_start_alias": COLD_START_CATEGORY_ALIASES.get(category, category),
            "cold_start_label": COLD_START_CATEGORY_LABELS.get(category, category),
        }
        return seed

    article["category"] = category
    article["cold_start_alias"] = COLD_START_CATEGORY_ALIASES.get(category, category)
    article["cold_start_label"] = COLD_START_CATEGORY_LABELS.get(category, category)
    return article


def _build_seed_items(feeds: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    seeds = []
    categories = _pick_cold_start_categories(feeds)
    for category in categories:
        seeds.append(_build_seed_item(feeds, category))
    return seeds


def _current_seed_item(profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    state = _ensure_cold_start_state(profile)
    seed_items = state.get("seed_items", [])
    if not seed_items:
        return None
    current_index = int(state.get("current_index", 0))
    if current_index >= len(seed_items):
        current_index = current_index % len(seed_items)
    if current_index < 0:
        current_index = 0
    state["current_index"] = current_index
    return seed_items[current_index]


def _selected_categories_text(selected_categories: List[str]) -> str:
    selected_text = "、".join(COLD_START_CATEGORY_LABELS.get(category, category) for category in selected_categories[-6:])
    if not selected_text:
        return "暂无"
    return selected_text


def _cold_start_action_buttons(profile: Dict[str, Any]) -> List[List[Dict[str, str]]]:
    state = _ensure_cold_start_state(profile)
    selected_count = len(state.get("selected_categories", []))
    ready_to_start = selected_count >= COLD_START_MIN_SELECTIONS
    return build_cold_start_buttons(selected_count=selected_count, ready_to_start=ready_to_start)


def _cold_start_header(profile: Dict[str, Any], item: Dict[str, Any]) -> str:
    state = _ensure_cold_start_state(profile)
    selected_categories = state.get("selected_categories", [])
    selected_count = len(selected_categories)
    index = int(state.get("current_index", 0)) + 1
    total = len(state.get("seed_items", []))
    label = item.get("cold_start_label", COLD_START_CATEGORY_LABELS.get(item.get("category", ""), "未分类"))
    alias = item.get("cold_start_alias", COLD_START_CATEGORY_ALIASES.get(item.get("category", ""), "unknown"))
    selected_text = _selected_categories_text(selected_categories)
    if selected_count < COLD_START_MIN_SELECTIONS:
        hint = "请先选满 2 个感兴趣领域（可点分类按钮，或对当前领域点 👍）。"
    elif selected_count < COLD_START_MAX_SELECTIONS:
        hint = "已满足最少 2 类，可点击 ✅ 开始推荐，或再补选 1 个领域。"
    else:
        hint = "已选满 3 类，正在进入智能推荐。"

    return (
        "👋 欢迎来到刷博客！我先推几篇不同领域的内容，帮你快速建立口味画像。\n"
        "冷启动进度：已选 {0}/{1}-{2} 个感兴趣领域（第 {3}/{4} 个领域）\n"
        "当前领域：{5}（{6}）\n"
        "已选领域：{7}\n"
        "操作提示：{8}\n\n".format(
            selected_count,
            COLD_START_MIN_SELECTIONS,
            COLD_START_MAX_SELECTIONS,
            index,
            max(1, total),
            label,
            alias,
            selected_text,
            hint,
        )
    )


def _cold_start_response(user_id: str, profile: Dict[str, Any], feeds: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    state = _ensure_cold_start_state(profile)
    if not state.get("seed_items"):
        state["seed_items"] = _build_seed_items(feeds)
        state["current_index"] = 0

    item = _current_seed_item(profile)
    if not item:
        item = _build_mock_item(feeds)
        item["category"] = "unknown"
        item["cold_start_alias"] = "unknown"
        item["cold_start_label"] = "未分类"

    profile["last_item"] = item
    _save_profile(user_id, profile)
    _safe_log_event(user_id, "cold_start_view", item, metadata={"mode": "cold_start"})

    return {
        "message": _cold_start_header(profile, item) + _build_card_message(item),
        "buttons": _cold_start_action_buttons(profile),
    }


def _complete_cold_start(
    user_id: str,
    profile: Dict[str, Any],
    feeds: Dict[str, List[Dict[str, Any]]],
    trigger: str,
    item: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    state = _ensure_cold_start_state(profile)
    selected_categories = list(state.get("selected_categories", []))
    state["active"] = False
    state["completed"] = True
    state["seed_items"] = []
    state["current_index"] = 0

    _activate_quick_learning(profile)
    _save_profile(user_id, profile)
    _safe_log_event(
        user_id,
        "cold_start_complete",
        item or profile.get("last_item", {}),
        metadata={"selected_categories": selected_categories, "trigger": trigger},
    )
    response = _next_item_response(user_id, profile, feeds)
    response["message"] = "✅ 冷启动完成，已进入智能推荐。\n已选领域：{0}\n\n{1}".format(
        _selected_categories_text(selected_categories),
        response["message"],
    )
    return response


def _choose_cold_start_category(
    user_id: str,
    profile: Dict[str, Any],
    feeds: Dict[str, List[Dict[str, Any]]],
    alias: str,
) -> Dict[str, Any]:
    normalized_alias = alias.strip().lower()
    category = COLD_START_ALIAS_TO_CATEGORY.get(normalized_alias, "")
    if not category:
        return {
            "message": "未识别的兴趣标签：{0}。可选：tech/ai/biz/design/science/popular".format(normalized_alias),
            "buttons": _cold_start_action_buttons(profile),
        }

    state = _ensure_cold_start_state(profile)
    selected = state.get("selected_categories", [])
    if category in selected:
        response = _cold_start_response(user_id, profile, feeds)
        response["message"] = "✅ 领域“{0}”已在已选列表中。\n\n{1}".format(
            COLD_START_CATEGORY_LABELS.get(category, category),
            response["message"],
        )
        return response

    if len(selected) >= COLD_START_MAX_SELECTIONS:
        return _complete_cold_start(
            user_id=user_id,
            profile=profile,
            feeds=feeds,
            trigger="choose_limit_reached",
        )

    selected.append(category)
    state["selected_categories"] = selected[:COLD_START_MAX_SELECTIONS]
    profile = _update_interest_tags(profile, _category_interest_tags(category), 4)

    # Move cursor to the selected category card, so next like/skip remains intuitive.
    for idx, seed in enumerate(state.get("seed_items", [])):
        if isinstance(seed, dict) and seed.get("category") == category:
            state["current_index"] = idx
            break

    _safe_log_event(
        user_id,
        "cold_start_choose",
        profile.get("last_item", {}),
        metadata={"alias": normalized_alias, "category": category, "selected_categories": list(state["selected_categories"])},
    )

    if len(state.get("selected_categories", [])) >= COLD_START_MAX_SELECTIONS:
        return _complete_cold_start(
            user_id=user_id,
            profile=profile,
            feeds=feeds,
            trigger="choose_max_selected",
        )

    _save_profile(user_id, profile)
    response = _cold_start_response(user_id, profile, feeds)
    if len(state.get("selected_categories", [])) >= COLD_START_MIN_SELECTIONS:
        response["message"] = "✅ 已选择领域：{0}。你已满足最少 2 类，可点 ✅ 开始推荐。\n\n{1}".format(
            COLD_START_CATEGORY_LABELS.get(category, category),
            response["message"],
        )
    else:
        response["message"] = "✅ 已选择领域：{0}，继续再选至少 1 类。\n\n{1}".format(
            COLD_START_CATEGORY_LABELS.get(category, category),
            response["message"],
        )
    return response


def _advance_cold_start(
    user_id: str,
    profile: Dict[str, Any],
    feeds: Dict[str, List[Dict[str, Any]]],
    action: str,
) -> Dict[str, Any]:
    state = _ensure_cold_start_state(profile)
    item = _current_seed_item(profile) or {}
    state = _ensure_cold_start_state(profile)
    category = item.get("category", "")

    if action == "like" and category:
        selected = state.get("selected_categories", [])
        if category not in selected and len(selected) < COLD_START_MAX_SELECTIONS:
            selected.append(category)
        state["selected_categories"] = selected[:COLD_START_MAX_SELECTIONS]
        profile = _update_interest_tags(profile, _category_interest_tags(category), 3)
        _safe_log_event(
            user_id,
            "cold_start_like",
            item,
            metadata={"selected_categories": list(selected)},
        )
    else:
        _safe_log_event(user_id, "cold_start_skip", item, metadata={"action": action})

    seen = state.get("seen_categories", [])
    if category and category not in seen:
        seen.append(category)
    state["seen_categories"] = seen[-COLD_START_MAX_CATEGORIES:]

    total = len(state.get("seed_items", []))
    if total > 0:
        state["current_index"] = (int(state.get("current_index", 0)) + 1) % total

    selected_count = len(state.get("selected_categories", []))
    if selected_count >= COLD_START_MAX_SELECTIONS:
        response = _complete_cold_start(
            user_id=user_id,
            profile=profile,
            feeds=feeds,
            trigger="like_max_selected",
            item=item,
        )
        return response

    _save_profile(user_id, profile)
    response = _cold_start_response(user_id, profile, feeds)
    if action == "like":
        if selected_count >= COLD_START_MIN_SELECTIONS:
            response["message"] = "✅ 已记录该领域偏好（+3），已可点击 ✅ 开始推荐。\n\n" + response["message"]
        else:
            response["message"] = "✅ 已记录该领域偏好（+3）\n\n" + response["message"]
    else:
        response["message"] = "⏭️ 已切换到下一个领域\n\n" + response["message"]
    return response


def _next_item_response(user_id: str, profile: Dict[str, Any], feeds: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    learning = _ensure_learning_state(profile)
    weights = _resolve_recommend_weights(profile)
    card_item = _build_recommended_item(feeds, profile=profile, weights=weights)
    profile["last_item"] = card_item
    profile = _record_read_history(profile, card_item.get("item_key", ""))
    profile = _record_source_history(profile, card_item.get("source", ""))

    quick_hint = ""
    if learning.get("phase") == "quick":
        learning["interaction_count"] = int(learning.get("interaction_count", 0)) + 1
        current_count = int(learning["interaction_count"])
        quick_limit = int(learning.get("quick_limit", QUICK_LEARN_INTERACTIONS))

        if current_count % QUICK_LEARN_REBALANCE_INTERVAL == 0 and current_count > int(learning.get("last_rebalanced_at", 0)):
            profile = _recalibrate_interest_tags(profile)
            learning["last_rebalanced_at"] = current_count
            _safe_log_event(
                user_id,
                "quick_learn_rebalance",
                card_item,
                metadata={"interaction_count": current_count},
            )

        if current_count >= quick_limit:
            learning["phase"] = "stable"
            quick_hint = "🎯 已进入稳定推荐模式。\n\n"
        else:
            quick_hint = "🧪 还在了解你的口味...（学习期 {0}/{1}）\n\n".format(current_count, quick_limit)

    profile["learning"] = learning
    _save_profile(user_id, profile)
    _safe_log_event(
        user_id,
        "view",
        card_item,
        metadata={
            "learning_phase": learning.get("phase", ""),
            "learning_interaction_count": learning.get("interaction_count", 0),
            "recommend_weights": weights,
        },
    )

    response = _build_brush_response(card_item)
    if quick_hint:
        response["message"] = quick_hint + response["message"]
    return response


def _merge_command_and_args(command: str, args: List[str]) -> str:
    if args and command.startswith("/"):
        return "{0} {1}".format(command, " ".join(args))
    return command


def _safe_log_event(
    user_id: str, action: str, item: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Log behavior event safely without affecting main command flow."""
    try:
        log_behavior_event(
            events_path=BEHAVIOR_EVENTS_FILE,
            user_id=user_id,
            action=action,
            item=item,
            metadata=metadata,
        )
    except Exception:
        # Behavior logging should not break command handling.
        return


def _is_true(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def _resolve_notion_config(context: Dict[str, Any]) -> Dict[str, Any]:
    sink_context = context.get("sink", {}) if isinstance(context.get("sink", {}), dict) else {}
    notion_context = sink_context.get("notion", {}) if isinstance(sink_context.get("notion", {}), dict) else {}

    enabled = notion_context.get("enabled", os.getenv("BRUSH_NOTION_ENABLED", "false"))
    api_key = notion_context.get("api_key", os.getenv("BRUSH_NOTION_API_KEY", ""))
    database_id = notion_context.get("database_id", os.getenv("BRUSH_NOTION_DATABASE_ID", ""))
    timeout_raw = notion_context.get("timeout", os.getenv("BRUSH_NOTION_TIMEOUT", "10"))
    try:
        timeout = int(timeout_raw)
    except Exception:
        timeout = 10

    return {
        "enabled": _is_true(enabled),
        "api_key": str(api_key or "").strip(),
        "database_id": str(database_id or "").strip(),
        "timeout": max(3, timeout),
    }


def _save_knowledge_note(user_id: str, item: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    note = build_structured_note(item=item, user_id=user_id)
    notion_config = _resolve_notion_config(context)
    return save_note(note=note, notion_config=notion_config, local_path=SAVED_NOTES_FILE)


def _build_save_feedback(sink_result: Dict[str, Any]) -> str:
    status = sink_result.get("status", "")
    if status == "saved_notion":
        return "🧠 已沉淀到 Notion（本地已备份）"
    if status == "saved_local_with_notion_error":
        return "🗂️ 已沉淀到本地知识库（Notion 暂不可用）"
    if status == "save_sink_error":
        return "⚠️ 收藏已成功，但知识沉淀失败（稍后可重试）"
    return "🗂️ 已沉淀到本地知识库"


def _build_deep_read_payload(item: Dict[str, Any]) -> Dict[str, str]:
    """
    Build deep-read payload from full article content with fallback.
    """
    title = str(item.get("title", "Untitled"))
    summary = str(item.get("summary", "暂无摘要"))
    link = str(item.get("link", "") or "")

    if not link:
        explain = build_plain_language_explanation(title, summary, summary)
        return {
            "explain": explain,
            "excerpt": summarize_text(summary, max_sentences=3, max_chars=420),
            "status": "no_link_fallback",
        }

    try:
        result = fetch_full_article_text(
            link,
            timeout=DEEP_READ_FETCH_TIMEOUT_SECONDS,
            max_chars=6500,
        )
        body_text = result.get("text", "")
        if body_text:
            explain = build_plain_language_explanation(title, summary, body_text)
            excerpt = build_deep_read_snippet(body_text, max_chars=900)
            return {
                "explain": explain,
                "excerpt": excerpt,
                "status": result.get("status", "ok"),
            }
    except Exception:
        pass

    explain = build_plain_language_explanation(title, summary, summary)
    return {
        "explain": explain,
        "excerpt": summarize_text(summary, max_sentences=3, max_chars=420),
        "status": "fetch_failed_fallback",
    }


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
    _ensure_cold_start_state(profile)
    _ensure_learning_state(profile)

    # 主命令：开始刷博客
    if command == "/brush":
        feeds = _load_feeds_cached()
        if _is_cold_start_active(profile):
            return _cold_start_response(user_id, profile, feeds)
        return _next_item_response(user_id, profile, feeds)

    elif command.startswith("/brush choose"):
        feeds = _load_feeds_cached()
        if not _is_cold_start_active(profile):
            return {"message": "冷启动已完成，直接用 /brush 刷推荐即可。", "buttons": build_brush_buttons()}
        parts = command.split()
        alias = parts[2].strip().lower() if len(parts) >= 3 else ""
        if not alias:
            return {
                "message": "请指定兴趣标签：tech/ai/biz/design/science/popular",
                "buttons": _cold_start_action_buttons(profile),
            }
        return _choose_cold_start_category(user_id, profile, feeds, alias)

    elif command == "/brush start":
        feeds = _load_feeds_cached()
        if not _is_cold_start_active(profile):
            return {"message": "你已在智能推荐模式，直接使用 /brush 即可。", "buttons": build_brush_buttons()}
        state = _ensure_cold_start_state(profile)
        selected_count = len(state.get("selected_categories", []))
        if selected_count < COLD_START_MIN_SELECTIONS:
            response = _cold_start_response(user_id, profile, feeds)
            response["message"] = "还差 {0} 个兴趣领域，先完成选择再开始推荐。\n\n{1}".format(
                COLD_START_MIN_SELECTIONS - selected_count,
                response["message"],
            )
            return response
        return _complete_cold_start(
            user_id=user_id,
            profile=profile,
            feeds=feeds,
            trigger="manual_start",
            item=profile.get("last_item", {}) if isinstance(profile.get("last_item", {}), dict) else {},
        )
    
    # 按钮回调处理
    elif command == "/brush like":
        feeds = _load_feeds_cached()
        if _is_cold_start_active(profile):
            return _advance_cold_start(user_id, profile, feeds, action="like")
        last_item = profile.get("last_item", {}) if isinstance(profile.get("last_item", {}), dict) else {}
        tags = last_item.get("tags", []) if isinstance(last_item.get("tags", []), list) else []
        profile = _update_interest_tags(profile, tags, delta=2)
        _save_profile(user_id, profile)
        _safe_log_event(user_id, "like", last_item)
        response = _next_item_response(user_id, profile, feeds)
        response["message"] = "✅ 已记录偏好（+2）\n\n" + response["message"]
        return response
    
    elif command == "/brush skip":
        feeds = _load_feeds_cached()
        if _is_cold_start_active(profile):
            return _advance_cold_start(user_id, profile, feeds, action="skip")
        last_item = profile.get("last_item", {}) if isinstance(profile.get("last_item", {}), dict) else {}
        tags = last_item.get("tags", []) if isinstance(last_item.get("tags", []), list) else []
        profile = _update_interest_tags(profile, tags, delta=-1)
        _save_profile(user_id, profile)
        _safe_log_event(user_id, "skip", last_item)
        response = _next_item_response(user_id, profile, feeds)
        response["message"] = "⏭️ 已跳过（-1）\n\n" + response["message"]
        return response
    
    elif command == "/brush read":
        action_buttons = _cold_start_action_buttons(profile) if _is_cold_start_active(profile) else build_brush_buttons()
        last_item = profile.get("last_item", {}) if isinstance(profile.get("last_item", {}), dict) else {}
        if not last_item:
            _safe_log_event(user_id, "read_miss", metadata={"reason": "no_last_item"})
            return {"message": "还没有可展开的文章，先试试 /brush", "buttons": action_buttons}
        deep_read_payload = _build_deep_read_payload(last_item)
        _safe_log_event(user_id, "read", last_item, metadata={"deep_read_status": deep_read_payload.get("status", "")})
        return {
            "message": build_deep_read_message(
                last_item,
                deep_read_summary=deep_read_payload.get("explain", ""),
                deep_read_excerpt=deep_read_payload.get("excerpt", ""),
            ),
            "buttons": action_buttons,
        }
    
    elif command == "/brush save":
        if _is_cold_start_active(profile):
            _safe_log_event(user_id, "cold_start_save_blocked", metadata={"reason": "cold_start_not_completed"})
            return {
                "message": "冷启动进行中，请先用 👍 选择至少 2 个感兴趣领域，再使用收藏。",
                "buttons": _cold_start_action_buttons(profile),
            }
        last_item = profile.get("last_item", {}) if isinstance(profile.get("last_item", {}), dict) else {}
        if not last_item:
            _safe_log_event(user_id, "save_miss", metadata={"reason": "no_last_item"})
            return {"message": "还没有可收藏的文章，先试试 /brush", "buttons": build_brush_buttons()}
        profile = _record_saved_item(profile, last_item)
        profile = _update_interest_tags(
            profile,
            last_item.get("tags", []) if isinstance(last_item.get("tags", []), list) else [],
            delta=5,
        )
        _save_profile(user_id, profile)
        try:
            sink_result = _save_knowledge_note(user_id, last_item, context)
        except Exception as exc:
            sink_result = {"status": "save_sink_error", "stores": [], "error": str(exc)}
        _safe_log_event(
            user_id,
            "save",
            last_item,
            metadata={
                "sink_status": sink_result.get("status", ""),
                "sink_stores": sink_result.get("stores", []),
            },
        )
        save_message = build_saved_message(last_item) + "\n" + _build_save_feedback(sink_result)
        return {"message": save_message, "buttons": build_brush_buttons()}
    
    elif command == "/brush refresh":
        feeds = _load_feeds_cached()
        if _is_cold_start_active(profile):
            return _advance_cold_start(user_id, profile, feeds, action="refresh")
        _safe_log_event(
            user_id,
            "refresh",
            profile.get("last_item", {}) if isinstance(profile.get("last_item", {}), dict) else {},
        )
        response = _next_item_response(user_id, profile, feeds)
        response["message"] = "🔄 已换一批\n\n" + response["message"]
        return response
    
    else:
        return {"message": "未知命令，试试 /brush"}


# CLI 入口（本地测试用）
def run_brush() -> int:
    """Handle /brush command with priority RSS source and fallback."""
    result = handle_command("/brush", [], "cli-user", {})
    print(result.get("message", ""))
    buttons = result.get("buttons", [])
    if buttons:
        button_texts = []
        for row in buttons:
            row_labels = " ".join("[{0}]".format(btn.get("text", "")) for btn in row)
            button_texts.append(row_labels)
        print("按钮：" + " | ".join(button_texts))
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
