# util/openai_client.py

import os
from functools import lru_cache
from openai import OpenAI, AsyncOpenAI

def _get(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v is not None else default

# 기존 동기 클라이언트 (네 코드 그대로)
@lru_cache
def openai_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    base_url = os.getenv("OPENAI_BASE_URL")
    timeout = float(_get("OPENAI_TIMEOUT", "30"))
    max_retries = int(_get("OPENAI_MAX_RETRIES", "2"))
    organization = os.getenv("OPENAI_ORG") or None
    project = os.getenv("OPENAI_PROJECT") or None

    if base_url:
        return OpenAI(
            api_key=key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            organization=organization,
            project=project,
        )
    return OpenAI(
        api_key=key,
        timeout=timeout,
        max_retries=max_retries,
        organization=organization,
        project=project,
    )

# 추가: 비동기 클라이언트
@lru_cache
def openai_async_client() -> AsyncOpenAI:
    """
    비동기 OpenAI SDK 클라이언트.
    - OPENAI_API_KEY: 필수
    - OPENAI_BASE_URL: 선택 (프록시/자체 게이트웨이 사용 시)
    - OPENAI_TIMEOUT: 기본 30초
    - OPENAI_MAX_RETRIES: 기본 2회
    - OPENAI_ORG / OPENAI_PROJECT: 선택
    """
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    base_url = os.getenv("OPENAI_BASE_URL")
    timeout = float(_get("OPENAI_TIMEOUT", "30"))
    max_retries = int(_get("OPENAI_MAX_RETRIES", "2"))
    organization = os.getenv("OPENAI_ORG") or None
    project = os.getenv("OPENAI_PROJECT") or None

    if base_url:
        return AsyncOpenAI(
            api_key=key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            organization=organization,
            project=project,
        )
    return AsyncOpenAI(
        api_key=key,
        timeout=timeout,
        max_retries=max_retries,
        organization=organization,
        project=project,
    )
