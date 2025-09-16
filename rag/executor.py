from __future__ import annotations
import json
from typing import Any, Dict, List
from .cache import TTLCache
from .errors import map_error, UserFacingError
from .normalizers import items_or_empty
from .paging import paginate

from tourapi.client import TourAPIClient

class ToolExecutor:
    """
    LLM tool_calls를 받아 TourAPIClient 메서드를 실행하고,
    LLM이 이해할 수 있는 tool 메시지(OpenAI 호환)로 변환한다.
    """
    def __init__(self, api_key: str, *, app_name: str = "Nomadly", timeout: float = 10.0, cache_ttl: int = 120) -> None:
        self._client = TourAPIClient(api_key=api_key, app_name=app_name, timeout=timeout)
        self._cache = TTLCache(ttl_seconds=cache_ttl)

    async def close(self) -> None:
        await self._client.close()

    async def _dispatch(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "get_location_based_list":
            return await self._call_with_cache(name, args, self._client.get_location_based_list)
        if name == "get_search_keyword":
            return await self._call_with_cache(name, args, self._client.get_search_keyword)
        if name == "get_detail_common":
            return await self._call_with_cache(name, args, self._client.get_detail_common)
        raise UserFacingError(f"지원하지 않는 도구: {name}")

    async def _call_with_cache(self, name: str, args: Dict[str, Any], fn) -> Dict[str, Any]:
        cached = await self._cache.get(name, args)
        if cached is not None:
            return cached
        try:
            res = await fn(**args)
            await self._cache.set(name, args, res)
            return res
        except Exception as e:
            raise map_error(e)

    async def consume_tool_calls(self, llm_resp: Any) -> List[Dict[str, Any]]:
        """
        OpenAI Chat 호환 응답 객체에서 tool_calls를 실행하고, {role:"tool", ...} 메시지 리스트 반환
        """
        out: List[Dict[str, Any]] = []
        choice = getattr(llm_resp, "choices", [None])[0]
        if not choice:
            return out
        message = getattr(choice, "message", None) or getattr(choice, "delta", None)
        if not message:
            return out
        tool_calls = getattr(message, "tool_calls", None) or []

        for tc in tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            try:
                res = await self._dispatch(name, args)
                content = json.dumps(res, ensure_ascii=False)
            except UserFacingError as ue:
                content = json.dumps({"error": str(ue)}, ensure_ascii=False)

            out.append({
                "role": "tool",
                "tool_call_id": getattr(tc, "id", None),
                "name": name,
                "content": content,
            })
        return out

    async def run_paged(self, name: str, args: Dict[str, Any], *, max_pages: int = 3) -> List[Dict[str, Any]]:
        async def fetch(p):
            return await self._dispatch(name, p)
        collected: List[Dict[str, Any]] = []
        async for page in paginate(fetch, args, max_pages=max_pages):
            collected.extend(items_or_empty(page))
        return collected
