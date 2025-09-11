import uuid

from fastapi import APIRouter, Depends

from mypage.service import mypage as service
from user.controller.user import get_current_user_id

router = APIRouter(prefix="/api/me")

@router.get("/plans")
def get_plans(
        user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    return service.get_plans(user_id)

@router.get("/bookmark/place")
def get_bookmark_place(
        user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    return service.get_bookmark_place(user_id)

@router.get("/like/board")
def get_bookmark_plans(
        user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    return service.get_bookmark_plans(user_id)