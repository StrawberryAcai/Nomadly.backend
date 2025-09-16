# plan/controller/ai_plan.py
from __future__ import annotations
from fastapi import APIRouter, Header, HTTPException
from plan.model.request.plan import PlanRequest as AIPlanRequest
from plan.model.response.plan import AIPlanResponse
from plan.service.plan import generate_ai_plan

router = APIRouter(prefix="/api/plan", tags=["plan"])

@router.post("/", response_model=AIPlanResponse)
async def ai_auto_complete(req: AIPlanRequest, Accept_Timezone: str | None = Header(default=None, alias="Accept-Timezone")):
    """
    AI 일정 자동완성.
    - 헤더 Accept-Timezone으로 응답 시간대 지정 (예: Asia/Seoul, UTC)
    - 본문은 명세의 필드를 그대로 따른다.
    """
    try:
        return await generate_ai_plan(req, Accept_Timezone)
    except Exception as e:
        # 사용자에게 너무 내부적인 에러를 드러내지 않도록 메시지는 간결하게
        raise HTTPException(status_code=500, detail=f"failed to generate plan: {e}")
