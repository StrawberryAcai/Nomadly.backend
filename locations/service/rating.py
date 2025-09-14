from uuid import UUID
from fastapi import HTTPException
from locations.repository.rating import RatingRepository
from locations.model.request.rating import RatingRequest
from locations.model.response.rating import RatingResponse

class RatingService:
    def __init__(self) -> None:
        self.repo = RatingRepository()

    def get_rating(self, place_id: UUID) -> RatingResponse:
        rating_info = self.repo.get_rating_by_place_id(place_id)
        if not rating_info:
            return RatingResponse(place_id=place_id, average_rating=0.0, total_ratings=0)
        return rating_info

    def add_rating(self, req: RatingRequest, current_user_id: UUID) -> RatingResponse:
        if current_user_id != req.user_id:
            raise HTTPException(status_code=403, detail="요청 사용자와 세션 사용자가 일치하지 않습니다.")
        try:
            self.repo.add_rating(place_id=req.place_id, score=req.score, user_id=req.user_id)
            updated = self.repo.refresh_rating_aggregates(req.place_id)
            return updated
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"평점 추가 중 오류 발생: {str(e)}")
