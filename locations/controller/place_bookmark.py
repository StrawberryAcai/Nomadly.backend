from fastapi import APIRouter, HTTPException, Body, Path, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from uuid import UUID
from locations.model.request.bookmark import BookmarkRequest
from locations.model.response.bookmark import BookmarkResponse
from locations.service.bookmark import BookmarkService

router = APIRouter(
    prefix="/api/locations/bookmark",
    tags=["북마크"],
    responses={500: {"description": "서버 내부 오류"}},
)

# 인증 설정
security = HTTPBearer(auto_error=False)

class CurrentUser(BaseModel):
    user_id: UUID

def _get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> CurrentUser:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다.")
    token = credentials.credentials
    try:
        # 프로젝트의 토큰 유틸에 맞게 디코드/검증
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
    try:
        return CurrentUser(user_id=UUID(str(uid)))
    except Exception:
        raise HTTPException(status_code=401, detail="토큰의 사용자 ID가 유효하지 않습니다.")

@router.get(
    "/{place_id}/{user_id}",
    response_model=BookmarkResponse,
    summary="북마크 상태 조회",
    description="특정 장소에 대해 사용자의 북마크 여부를 확인합니다.",
    response_description="북마크 상태 응답",
    responses={
        200: {
            "description": "성공",
            "content": {
                "application/json": {
                    "example": {
                        "place_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                        "user_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                        "is_bookmarked": True
                    }
                }
            }
        }
    },
)
async def get_bookmark_status(
    place_id: UUID = Path(..., description="장소 ID"),
    user_id: UUID = Path(..., description="사용자 ID"),
    current: CurrentUser = Depends(_get_current_user),
):
    service = BookmarkService()
    return service.get_status(place_id=place_id, user_id=user_id, current_user_id=current.user_id)

@router.post(
    "/",
    response_model=BookmarkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="북마크 추가",
    description="사용자의 장소 북마크를 추가합니다.",
    response_description="추가된 북마크 상태",
    responses={
        201: {
            "description": "생성됨",
            "content": {
                "application/json": {
                    "example": {
                        "place_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                        "user_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                        "is_bookmarked": True
                    }
                }
            }
        }
    },
)
async def add_bookmark(
    req: BookmarkRequest = Body(
        ...,
        description="북마크 추가 요청 바디",
        examples={
            "기본": {
                "summary": "북마크 추가 예시",
                "value": {
                    "place_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "user_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
                }
            }
        },
    ),
    current: CurrentUser = Depends(_get_current_user),
):
    service = BookmarkService()
    return service.add_bookmark(req, current_user_id=current.user_id)

@router.delete(
    "/",
    response_model=BookmarkResponse,
    status_code=status.HTTP_200_OK,
    summary="북마크 삭제",
    description="사용자의 장소 북마크를 삭제합니다.",
    response_description="삭제된 북마크 상태",
    responses={
        200: {
            "description": "성공",
            "content": {
                "application/json": {
                    "example": {
                        "place_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                        "user_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                        "is_bookmarked": False
                    }
                }
            }
        }
    },
)
async def remove_bookmark(
    req: BookmarkRequest = Body(
        ...,
        description="북마크 삭제 요청 바디",
        examples={
            "기본": {
                "summary": "북마크 삭제 예시",
                "value": {
                    "place_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "user_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
                }
            }
        },
    ),
    current: CurrentUser = Depends(_get_current_user),
):
    service = BookmarkService()
    return service.remove_bookmark(req, current_user_id=current.user_id)