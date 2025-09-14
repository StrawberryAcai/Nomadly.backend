from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from locations.service.locations import recommend

router = APIRouter(prefix="/api")

# 콘텐츠 타입 매핑
CONTENTTYPE = {
    "관광지": 12,
    "문화시설": 14,
    "축제공연행사": 15,
    "여행코스": 25,
    "레포츠": 28,
    "숙박": 32,
    "쇼핑": 38,
    "음식점": 39
}

# 요청 모델
class RecommendRequest(BaseModel):
    type: str  # 콘텐츠 유형 (예: "관광지")
    longitude: float  # 사용자의 경도
    latitude: float  # 사용자의 위도

# 응답 모델
class RecommendResponse(BaseModel):
    place_name: str
    rating: float
    trend: bool
    bookmark_cnt: int
    distance: float
    image: str

@router.post("/locations", response_model=List[RecommendResponse])
async def locations(req: RecommendRequest):
    """
    사용자의 위치와 콘텐츠 유형을 기반으로 추천 장소를 반환합니다.
    """
    # 콘텐츠 유형 검증
    type_id = CONTENTTYPE.get(req.type)
    if not type_id:
        raise HTTPException(status_code=400, detail="유효하지 않은 콘텐츠 유형입니다.")

    try:
        # 추천 장소 가져오기
        recommendations = await recommend(type_id, req.longitude, req.latitude)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))