
import html
import re
from typing import List


def clean_text(text: str) -> str:
    """Normalize feed text for card display."""
    if not text:
        return ""

    cleaned = html.unescape(text)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def summarize_text(text: str, max_sentences: int = 3, max_chars: int = 220) -> str:
    """
    Build a short summary with 2-3 sentences for card rendering.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return "暂无摘要"

    sentence_candidates: List[str] = re.split(r"(?<=[。！？.!?])\s+", cleaned)
    sentences = [s.strip() for s in sentence_candidates if s.strip()]

    if sentences:
        summary = " ".join(sentences[:max_sentences]).strip()
    else:
        summary = cleaned

    if len(summary) > max_chars:
        summary = summary[: max_chars - 1].rstrip() + "…"

    return summary or "暂无摘要"
