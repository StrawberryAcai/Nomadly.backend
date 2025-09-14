from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from locations.repository.place_bookmark import BookmarkRepository

router = APIRouter(prefix="/api/locations/bookmark")

# 요청 모델
class BookmarkRequest(BaseModel):
    place_id: UUID  # 장소 ID
    user_id: UUID  # 사용자 ID

# 응답 모델
class BookmarkResponse(BaseModel):
    place_id: UUID
    user_id: UUID
    is_bookmarked: bool

@router.get("/{place_id}/{user_id}", response_model=BookmarkResponse)
async def get_bookmark_status(place_id: UUID, user_id: UUID):
    """
    특정 장소에 대한 사용자의 북마크 상태를 반환합니다.
    """
    bookmark_repo = BookmarkRepository()

    # 북마크 상태 확인
    is_bookmarked = bookmark_repo.is_bookmarked(place_id=place_id, user_id=user_id)
    return BookmarkResponse(place_id=place_id, user_id=user_id, is_bookmarked=is_bookmarked)

@router.post("/", response_model=BookmarkResponse)
async def add_bookmark(req: BookmarkRequest):
    """
    특정 장소에 북마크를 추가합니다.
    """
    bookmark_repo = BookmarkRepository()

    try:
        # 북마크 추가
        bookmark_repo.add_bookmark(place_id=req.place_id, user_id=req.user_id)
        return BookmarkResponse(place_id=req.place_id, user_id=req.user_id, is_bookmarked=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"북마크 추가 중 오류 발생: {str(e)}")

@router.delete("/", response_model=BookmarkResponse)
async def remove_bookmark(req: BookmarkRequest):
    """
    특정 장소에서 북마크를 삭제합니다.
    """
    bookmark_repo = BookmarkRepository()

    try:
        # 북마크 삭제
        bookmark_repo.remove_bookmark(place_id=req.place_id, user_id=req.user_id)
        return BookmarkResponse(place_id=req.place_id, user_id=req.user_id, is_bookmarked=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"북마크 삭제 중 오류 발생: {str(e)}")