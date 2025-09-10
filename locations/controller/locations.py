from fastapi import APIRouter, HTTPException, Depends
import



router = APIRouter(prefix="/api")

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

@router.post("/locations", response_model=RecommendResponse)
def locations(req: RecommendRequest):
