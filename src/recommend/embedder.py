"""Embedding placeholder for future milestones."""

from __future__ import annotations


def embed_text(text: str) -> list[float]:
    """Generate a toy embedding based on text length for M1."""
    size = max(1, min(len(text), 32))
    return [float(size)]
