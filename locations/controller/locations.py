from fastapi import APIRouter, HTTPException, Body, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from locations.service.locations import recommend
from locations.model.request.request import RecommendRequest
from locations.model.response.response import RecommendResponse
from locations.constants import CONTENTTYPE

router = APIRouter(prefix="/api", tags=["장소 추천"])
security = HTTPBearer(auto_error=False)


@router.post(
    "/locations",
    response_model=RecommendResponse,
    summary="사용자 위치 기반 장소 추천",
    description="요청한 콘텐츠 유형(type)과 기준 좌표(origin: 경도/위도)를 바탕으로 추천 장소 목록을 반환합니다.",
    response_description="추천 결과가 포함된 RecommendResponse를 반환합니다.",
    tags=["장소 추천"],
    responses={
        400: {
            "description": "유효하지 않은 콘텐츠 유형입니다.",
            "content": {
                "application/json": {
                    "examples": {
                        "invalidType": {
                            "summary": "지원하지 않는 type",
                            "value": {"detail": "유효하지 않은 콘텐츠 유형입니다."}
                        }
                    }
                }
            },
        },
        500: {
            "description": "내부 서버 오류",
            "content": {
                "application/json": {
                    "examples": {
                        "serverError": {
                            "summary": "예상치 못한 오류",
                            "value": {"detail": "서버 내부 오류가 발생했습니다."}
                        }
                    }
                }
            },
        },
    },
)
async def locations(
    req: RecommendRequest = Body(
        ...,
        title="추천 요청 본문",
        description="추천을 위한 콘텐츠 유형과 기준 좌표를 전달합니다.",
        examples={
            "tourExample": {
                "summary": "관광지 추천 요청",
                "value": {
                    "type": "관광지",
                    "origin": {"longitude": 126.9780, "latitude": 37.5665}
                }
            },
            "foodExample": {
                "summary": "맛집 추천 요청",
                "value": {
                    "type": "맛집",
                    "origin": {"longitude": 129.0756, "latitude": 35.1796}
                }
            }
        },
    ),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    # 콘텐츠 유형 검증
    type_id = CONTENTTYPE.get(req.type)
    if not type_id:
        raise HTTPException(status_code=400, detail="유효하지 않은 콘텐츠 유형입니다.")

    try:
        # Authorization 헤더 추출
        auth_header = f"Bearer {credentials.credentials}" if credentials else None
        # RecommendResponse 객체 반환
        return await recommend(type_id, req.origin.longitude, req.origin.latitude, auth_header)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))