
from typing import Any, Union, Optional, Dict, List


def score_item(item: Dict[str, Any]) -> float:
    """Return a deterministic placeholder score for M1."""
    popularity = float(item.get("popularity", 0.5))
    diversity = float(item.get("diversity", 0.5))
    return popularity * 0.6 + diversity * 0.4
