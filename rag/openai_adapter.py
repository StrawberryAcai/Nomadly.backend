from __future__ import annotations
from typing import Any, Dict, List

class OpenAIChatTools:
    """
    OpenAI Chat Completions 호환 어댑터. 실제 SDK 인스턴스를 주입받아 호출한다.
    client는 openai.AsyncOpenAI 호환이어야 한다.
    """
    def __init__(self, model: str, *, client: Any) -> None:
        self.model = model
        self.client = client

    async def create_completion(self, *, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] | None = None, tool_choice: str | None = "auto") -> Any:
        # 주입된 client는 openai.AsyncOpenAI와 동일한 인터페이스여야 한다.
        return await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice
        )
