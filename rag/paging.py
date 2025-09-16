from __future__ import annotations
from typing import AsyncIterator, Callable, Dict, Any

async def paginate(
    fetch: Callable[[Dict[str, Any]], Any],
    base_params: Dict[str, Any],
    *, page_param: str = "page_no", size_param: str = "num_of_rows",
    start_page: int = 1, max_pages: int = 5
) -> AsyncIterator[Any]:
    params = dict(base_params)
    page = params.get(page_param, start_page) or start_page
    size = params.get(size_param)
    for _ in range(max_pages):
        params[page_param] = page
        res = await fetch(params)
        yield res
        try:
            body = res["response"]["body"]
            total = int(body.get("totalCount", 0))
            page_no = int(body.get("pageNo", page))
            num_rows = int(body.get("numOfRows", size or 10))
            if page_no * num_rows >= total:
                break
        except Exception:
            break
        page += 1
