from __future__ import annotations
from typing import Any, Dict, List

def items_or_empty(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        items = data["response"]["body"]["items"]["item"]
        if isinstance(items, list):
            return items
        return [items]
    except Exception:
        return []
