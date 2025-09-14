from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from locations.repository.rating import RatingRepository

router = APIRouter(prefix="/api/locations/rating")

# 요청 모델
class RatingRequest(BaseModel):
    place_id: UUID  # 장소 ID
    score: float  # 평점 (0.0 ~ 5.0)

# 응답 모델
class RatingResponse(BaseModel):
    place_id: UUID
    average_rating: float
    total_ratings: int

@router.get("/{place_id}", response_model=RatingResponse)
async def get_rating(place_id: UUID):
    """
    특정 장소의 평점 정보를 반환합니다.
    """
    rating_repo = RatingRepository()

    # 장소 평점 가져오기
    rating_info = rating_repo.get_rating_by_place_id(place_id)
    if not rating_info:
        raise HTTPException(status_code=404, detail="해당 장소의 평점 정보가 없습니다.")

    return rating_info

@router.post("/", response_model=RatingResponse)
async def add_rating(req: RatingRequest):
    """
    특정 장소에 평점을 추가합니다.
    """
    rating_repo = RatingRepository()

    # 평점 추가
    try:
        rating_repo.add_rating(place_id=req.place_id, score=req.score)
        # 평점 추가 후 업데이트된 평점 정보 반환
        updated_rating = rating_repo.refresh_rating_aggregates(req.place_id)
        return updated_rating
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"평점 추가 중 오류 발생: {str(e)}")