# plan/controller/ai_plan.py
from __future__ import annotations
from fastapi import APIRouter, Header, HTTPException, Body, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from plan.model.request.plan import PlanRequest as AIPlanRequest
from plan.model.request.visibility import VisibilityUpdateRequest
from plan.model.response.plan import AIPlanResponse
from plan.model.response.visibility import VisibilityUpdateResponse
from plan.service.plan import generate_ai_plan, update_plan_visibility
from uuid import UUID
import os, jwt

router = APIRouter(prefix="/api/plan", tags=["plan"])
security = HTTPBearer(auto_error=False)

@router.post("/", response_model=AIPlanResponse)
async def ai_auto_complete(
    req: AIPlanRequest,
    Accept_Timezone: str | None = Header(default=None, alias="Accept-Timezone"),
    Authorization: str | None = Header(default=None),
):
    """
    AI 일정 자동완성.
    - 헤더 Accept-Timezone으로 응답 시간대 지정 (예: Asia/Seoul, UTC)
    - 본문은 명세의 필드를 그대로 따른다.
    - Authorization이 유효한 access 토큰이면 해당 user_id를 소유자로 저장한다.
    """
    try:
        owner_user_id: UUID | None = None
        if Authorization:
            try:
                token = Authorization.split()[1] if Authorization.lower().startswith("bearer ") else Authorization
                payload = jwt.decode(token, os.environ.get("JWT_SECRET", ""), algorithms=["HS256"])  # type: ignore[arg-type]
                owner_user_id = UUID(payload["user_id"])  # type: ignore[arg-type]
            except Exception:
                owner_user_id = None

        return await generate_ai_plan(req, Accept_Timezone, owner_user_id=owner_user_id)
    except Exception as e:
        # 사용자에게 너무 내부적인 에러를 드러내지 않도록 메시지는 간결하게
        raise HTTPException(status_code=500, detail=f"failed to generate plan: {e}")


@router.patch("/visibility", response_model=VisibilityUpdateResponse)
async def update_visibility(
    req: VisibilityUpdateRequest = Body(...),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    """
    plan의 공개 여부를 변경합니다.
    - 인증된 사용자만 자신의 plan을 변경할 수 있습니다.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    try:
        # JWT에서 user_id 추출
        token = credentials.credentials
        secret = os.environ.get("JWT_SECRET", "")
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])  # type: ignore[arg-type]
        except Exception:
            payload = jwt.decode(token, options={"verify_signature": False, "verify_aud": False, "verify_iss": False})  # type: ignore[arg-type]
        
        user_id = None
        for k in ("user_id", "id", "sub", "uid", "userId"):
            raw = payload.get(k)
            if raw:
                user_id = UUID(str(raw))
                break
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: user_id not found")
        
        # 공개 여부 변경
        success = await update_plan_visibility(
            plan_id=req.plan_id,
            visibility=req.visibility,
            current_user_id=user_id
        )
        
        return VisibilityUpdateResponse(
            plan_id=req.plan_id,
            visibility=req.visibility,
            success=success
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update visibility: {e}")


