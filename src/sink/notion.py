
from typing import Any, Union, Optional, Dict, List


def save_to_notion(note: Dict[str, Any]) -> Dict[str, Any]:
    """Fake Notion save response for M1."""
    return {"status": "stub", "note": note}
