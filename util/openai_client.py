import os
from functools import lru_cache
from openai import OpenAI

def _get(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v is not None else default

# 빠른 응답을 위해 캐싱 (동일한 인자 조합에 한해)
@lru_cache
def openai_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    # 필수
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    # 자체 서버, 프록시 등을 사용할때 원본 OpenAI API URL과 다르므로 그떄 BASE_URL 사용
    base_url = os.getenv("OPENAI_BASE_URL")
    timeout = float(_get("OPENAI_TIMEOUT", "30"))
    max_retries = int(_get("OPENAI_MAX_RETRIES", "2"))
    if base_url:
        return OpenAI(api_key=key, base_url=base_url, timeout=timeout, max_retries=max_retries)
    return OpenAI(api_key=key, timeout=timeout, max_retries=max_retries)
