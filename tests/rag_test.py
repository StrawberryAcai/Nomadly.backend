# tests/test_openai_smoke.py
import os
import pytest
from rag.schemas import TOOL_SCHEMAS
from util.openai_client import openai_async_client
from dotenv import load_dotenv

pytestmark = pytest.mark.asyncio
load_dotenv()

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
async def test_openai_can_see_tools_and_propose_calls():
    client = openai_async_client()
    # 메시지는 도구 필요성을 살짝 유도
    messages = [{"role": "user", "content": "서울 시청 근처 관광지 몇 개 추천해줘. 반경은 2000m 정도."}]
    resp = await client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages,
        tools=TOOL_SCHEMAS,
        tool_choice="auto",
    )
    # 도구 호출이 반드시 생긴다고 보장할 순 없지만,
    # 최소한 필드 접근이 정상이어야 한다.
    assert hasattr(resp.choices[0].message, "content")
    print("response")
    print(resp)
    # tool_calls가 생겼다면 구조가 정상인지 확인
    tcs = getattr(resp.choices[0].message, "tool_calls", None)
    if tcs:
        tc = tcs[0]
        assert hasattr(tc, "function")
        assert hasattr(tc.function, "name")
        assert hasattr(tc.function, "arguments")
