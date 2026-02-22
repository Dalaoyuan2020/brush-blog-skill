

from typing import List


def embed_text(text: str) -> List[float]:
    """Generate a toy embedding based on text length for M1."""
    size = max(1, min(len(text), 32))
    return [float(size)]
