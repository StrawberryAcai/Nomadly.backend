from uuid import UUID, uuid4
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
        # 메서드명 수정: is_bookmarked -> has_bookmark
        is_bookmarked = self.repo.has_bookmark(place_id=place_id, user_id=user_id)
        return BookmarkResponse(place_id=place_id, user_id=user_id, is_bookmarked=is_bookmarked)

    def add_bookmark(self, req: BookmarkRequest, current_user_id: UUID) -> BookmarkResponse:
        if current_user_id != req.user_id:
            raise HTTPException(status_code=403, detail="요청 사용자와 세션 사용자가 일치하지 않습니다.")
        # 사전 검증: place 존재 여부 확인 (FK 위반 방지)
        try:
            if not self.repo.places.get_place(req.place_id):
                raise HTTPException(status_code=404, detail="존재하지 않는 place_id입니다. 먼저 장소를 생성/조회하여 유효한 place_id를 사용하세요.")
        except HTTPException:
            raise
        except Exception as e:
            # DB 오류 등은 500으로 래핑
            raise HTTPException(status_code=500, detail=f"장소 조회 중 오류: {e}")
        try:
            # repository 시그니처에 맞게 bookmark_id 생성해 전달
            self.repo.add_bookmark(bookmark_id=uuid4(), place_id=req.place_id, user_id=req.user_id)
            return BookmarkResponse(place_id=req.place_id, user_id=req.user_id, is_bookmarked=True)
        except HTTPException:
            raise
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
