from uuid import UUID
from fastapi import HTTPException

from locations.repository.place_bookmark import BookmarkRepository
from locations.model.request.bookmark import BookmarkRequest
from locations.model.response.bookmark import BookmarkResponse

class BookmarkService:
    def __init__(self) -> None:
        self.repo = BookmarkRepository()

    def get_status(self, place_id: UUID, user_id: UUID, current_user_id: UUID) -> BookmarkResponse:
        if current_user_id != user_id:
            raise HTTPException(status_code=403, detail="요청 사용자와 세션 사용자가 일치하지 않습니다.")
        is_bookmarked = self.repo.is_bookmarked(place_id=place_id, user_id=user_id)
        return BookmarkResponse(place_id=place_id, user_id=user_id, is_bookmarked=is_bookmarked)

    def add_bookmark(self, req: BookmarkRequest, current_user_id: UUID) -> BookmarkResponse:
        if current_user_id != req.user_id:
            raise HTTPException(status_code=403, detail="요청 사용자와 세션 사용자가 일치하지 않습니다.")
        try:
            self.repo.add_bookmark(place_id=req.place_id, user_id=req.user_id)
            return BookmarkResponse(place_id=req.place_id, user_id=req.user_id, is_bookmarked=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"북마크 추가 중 오류 발생: {str(e)}")

    def remove_bookmark(self, req: BookmarkRequest, current_user_id: UUID) -> BookmarkResponse:
        if current_user_id != req.user_id:
            raise HTTPException(status_code=403, detail="요청 사용자와 세션 사용자가 일치하지 않습니다.")
        try:
            self.repo.remove_bookmark(place_id=req.place_id, user_id=req.user_id)
            return BookmarkResponse(place_id=req.place_id, user_id=req.user_id, is_bookmarked=False)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"북마크 삭제 중 오류 발생: {str(e)}")
