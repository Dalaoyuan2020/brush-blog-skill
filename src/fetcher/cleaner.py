
import re


def clean_text(text: str) -> str:
    """Normalize whitespace for card display."""
    normalized = re.sub(r"\s+", " ", text or "").strip()
    return normalized
