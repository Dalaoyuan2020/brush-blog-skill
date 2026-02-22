"""Simple recommendation scoring placeholder."""

from __future__ import annotations

from typing import Any


def score_item(item: dict[str, Any]) -> float:
    """Return a deterministic placeholder score for M1."""
    popularity = float(item.get("popularity", 0.5))
    diversity = float(item.get("diversity", 0.5))
    return popularity * 0.6 + diversity * 0.4
