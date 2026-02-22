"""Notion sink placeholder."""

from __future__ import annotations

from typing import Any


def save_to_notion(note: dict[str, Any]) -> dict[str, Any]:
    """Fake Notion save response for M1."""
    return {"status": "stub", "note": note}
