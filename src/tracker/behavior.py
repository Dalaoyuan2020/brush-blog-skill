import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union


@dataclass
class BehaviorEvent:
    user_id: str
    action: str
    item_id: str
    item_title: str = ""
    source: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "action": self.action,
            "item_id": self.item_id,
            "item_title": self.item_title,
            "source": self.source,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


def log_behavior_event(
    events_path: Union[str, Path],
    user_id: str,
    action: str,
    item: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> BehaviorEvent:
    """
    Append one behavior event into jsonl file.
    """
    item = item or {}
    metadata = metadata or {}
    item_id = item.get("item_key") or item.get("link") or item.get("title", "")
    tags = item.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    event = BehaviorEvent(
        user_id=user_id,
        action=action,
        item_id=str(item_id),
        item_title=str(item.get("title", "")),
        source=str(item.get("source", "")),
        tags=[str(tag) for tag in tags],
        metadata=metadata,
    )
    _append_event(events_path, event)
    return event


def read_recent_events(
    events_path: Union[str, Path], user_id: Optional[str] = None, limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Read recent events from jsonl file.
    """
    path = Path(events_path)
    if not path.exists():
        return []

    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if user_id and row.get("user_id") != user_id:
                continue
            rows.append(row)

    rows = rows[-max(1, int(limit)) :]
    return rows


def _append_event(events_path: Union[str, Path], event: BehaviorEvent) -> None:
    path = Path(events_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
