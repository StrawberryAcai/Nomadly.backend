import uuid

from fastapi import APIRouter, Depends

from mypage.model.mypage import MyPlansResponse
from mypage.service import mypage as service
from user.controller.user import get_current_user_id

router = APIRouter(prefix="/api/me")

@router.get("/plans", response_model=MyPlansResponse)
def get_plans(
        # user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    user_id = uuid.UUID("6ee53234-1dc5-44e8-8f3c-b2b98530aca6")
    return service.get_plans(user_id)

@router.get("/bookmark/place")
def get_bookmark_place(
        # user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    user_id = uuid.UUID("6ee53234-1dc5-44e8-8f3c-b2b98530aca6")
    return service.get_bookmark_place(user_id)

@router.get("/like/board")
def get_like_boards(
        # user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    user_id = uuid.UUID("6ee53234-1dc5-44e8-8f3c-b2b98530aca6")
    return service.get_like_boards(user_id)