from __future__ import annotations
import time, json, asyncio
from typing import Any, Dict, Tuple

class TTLCache:
    def __init__(self, ttl_seconds: int = 120) -> None:
        self._ttl = ttl_seconds
        self._data: Dict[str, Tuple[float, Any]] = {}
        self._lock = asyncio.Lock()

    def _key(self, name: str, payload: Dict[str, Any]) -> str:
        return f"{name}:{json.dumps(payload, sort_keys=True, ensure_ascii=False)}"

    async def get(self, name: str, payload: Dict[str, Any]) -> Any | None:
        k = self._key(name, payload)
        async with self._lock:
            v = self._data.get(k)
            if not v: return None
            ts, val = v
            if time.time() - ts > self._ttl:
                self._data.pop(k, None)
                return None
            return val

    async def set(self, name: str, payload: Dict[str, Any], value: Any) -> None:
        k = self._key(name, payload)
        async with self._lock:
            self._data[k] = (time.time(), value)
