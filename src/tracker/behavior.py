"""User behavior tracker placeholder."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class BehaviorEvent:
    user_id: str
    action: str
    item_id: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
