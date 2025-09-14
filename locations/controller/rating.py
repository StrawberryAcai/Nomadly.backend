from fastapi import APIRouter, HTTPException, Depends, Security, Body, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from uuid import UUID
from locations.model.request.rating import RatingRequest
from locations.model.response.rating import RatingResponse
from locations.service.rating import RatingService

router = APIRouter(prefix="/api/locations/rating", tags=["평점"])

security = HTTPBearer(auto_error=False)

class CurrentUser(BaseModel):
    user_id: UUID

def _get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> CurrentUser:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다.")
    token = credentials.credentials
    try:
        from auth.service.auth import token_factory
        try:
            payload = token_factory.decode(token)
        except Exception:
            payload = token_factory.verify(token)
    except Exception:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    uid = payload.get("user_id") or payload.get("sub") or payload.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="토큰에 사용자 정보가 없습니다.")
    return CurrentUser(user_id=UUID(str(uid)))

@router.get(
    "/{place_id}",
    response_model=RatingResponse,
    summary="장소 평점 조회",
    description="장소에 대한 평균 평점과 총 평가 수를 반환합니다.",
    responses={
        200: {
            "description": "성공적으로 평점을 조회했습니다.",
            "content": {
                "application/json": {
                    "example": {
                        "place_id": "11111111-1111-1111-1111-111111111111",
                        "average_rating": 4.2,
                        "total_ratings": 15
                    }
                }
            }
        }
    }
)
async def get_rating(place_id: UUID = Path(..., description="조회할 장소의 ID")):
    service = RatingService()
    return service.get_rating(place_id)

@router.post(
    "/",
    response_model=RatingResponse,
    summary="장소 평점 등록",
    description="사용자가 지정한 장소에 대한 평점을 추가하고, 갱신된 집계 결과를 반환합니다.",
    responses={
        200: {
            "description": "평점이 추가되고, 갱신된 집계 결과가 반환되었습니다.",
            "content": {
                "application/json": {
                    "example": {
                        "place_id": "11111111-1111-1111-1111-111111111111",
                        "average_rating": 4.0,
                        "total_ratings": 16
                    }
                }
            }
        },
        401: {
            "description": "인증 실패",
            "content": {"application/json": {"example": {"detail": "유효하지 않은 토큰입니다."}}}
        },
        403: {
            "description": "요청 사용자와 세션 사용자 불일치",
            "content": {"application/json": {"example": {"detail": "요청 사용자와 세션 사용자가 일치하지 않습니다."}}}
        },
        500: {
            "description": "서버 오류",
            "content": {"application/json": {"example": {"detail": "평점 추가 중 오류 발생: ..."}}}
        }
    }
)
async def add_rating(
    req: RatingRequest = Body(
        ...,
        description="추가할 평점 정보",
        examples={
            "valid": {
                "summary": "유효한 평점 요청",
                "value": {
                    "place_id": "11111111-1111-1111-1111-111111111111",
                    "user_id": "22222222-2222-2222-2222-222222222222",
                    "score": 5
                }
            }
        }
    ),
    current: CurrentUser = Depends(_get_current_user)
):
    service = RatingService()
    return service.add_rating(req, current.user_id)