from typing import Any, Dict, List, Sequence, Tuple


def score_item(
    item: Dict[str, Any],
    profile: Dict[str, Any],
    recent_sources: Sequence[str],
    weights: Dict[str, float],
) -> Tuple[float, Dict[str, float]]:
    """
    Score one candidate item with weighted components.
    """
    interest_score = _interest_component(item, profile)
    knowledge_score = _knowledge_component(item, profile)
    diversity_score = _diversity_component(item, recent_sources)
    popularity_score = _popularity_component(item)

    score = (
        interest_score * float(weights.get("interest", 0.4))
        + knowledge_score * float(weights.get("knowledge", 0.3))
        + diversity_score * float(weights.get("diversity", 0.2))
        + popularity_score * float(weights.get("popularity", 0.1))
    )
    score = round(score, 6)

    breakdown = {
        "interest": round(interest_score, 6),
        "knowledge": round(knowledge_score, 6),
        "diversity": round(diversity_score, 6),
        "popularity": round(popularity_score, 6),
        "total": score,
    }
    return score, breakdown


def rank_items(
    items: Sequence[Dict[str, Any]],
    profile: Dict[str, Any],
    recent_sources: Sequence[str],
    weights: Dict[str, float],
) -> List[Dict[str, Any]]:
    """
    Return items sorted by recommendation score descending.
    """
    ranked = []
    for item in items:
        score, breakdown = score_item(item, profile, recent_sources, weights)
        decorated = dict(item)
        decorated["score"] = score
        decorated["score_breakdown"] = breakdown
        ranked.append(decorated)

    ranked.sort(key=lambda value: value.get("score", 0.0), reverse=True)
    return ranked


def _interest_component(item: Dict[str, Any], profile: Dict[str, Any]) -> float:
    tags = item.get("tags", [])
    if not isinstance(tags, list) or not tags:
        return 0.0

    interest_tags = profile.get("interest_tags", {})
    if not isinstance(interest_tags, dict) or not interest_tags:
        return 0.2

    matched_scores = []
    for tag in tags:
        if tag in interest_tags:
            matched_scores.append(float(interest_tags.get(tag, 0.0)))
    if not matched_scores:
        return 0.1

    avg = sum(matched_scores) / max(len(matched_scores), 1)
    return min(1.0, avg / 5.0)


def _knowledge_component(item: Dict[str, Any], profile: Dict[str, Any]) -> float:
    """
    Placeholder knowledge relevance: overlap with saved item tags if available.
    """
    tags = set(item.get("tags", []) if isinstance(item.get("tags", []), list) else [])
    if not tags:
        return 0.0

    saved_items = profile.get("saved_items", [])
    if not isinstance(saved_items, list) or not saved_items:
        return 0.2

    matched = 0
    total = 0
    for saved in saved_items[-20:]:
        saved_summary = saved.get("summary", "") if isinstance(saved, dict) else ""
        saved_title = saved.get("title", "") if isinstance(saved, dict) else ""
        corpus = "{0} {1}".format(saved_title, saved_summary).lower()
        for tag in tags:
            total += 1
            if tag.lower() in corpus:
                matched += 1

    if total == 0:
        return 0.0
    return min(1.0, float(matched) / float(total))


def _diversity_component(item: Dict[str, Any], recent_sources: Sequence[str]) -> float:
    source = item.get("source", "")
    if not source:
        return 0.5
    if source in recent_sources:
        return 0.1
    return 1.0


def _popularity_component(item: Dict[str, Any]) -> float:
    category = item.get("category", "")
    if category == "priority_hn_popular_2025":
        return 1.0
    return 0.6
