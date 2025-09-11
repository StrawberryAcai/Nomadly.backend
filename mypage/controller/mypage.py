from fastapi import APIRouter

from mypage.service import mypage as service

router = APIRouter(prefix="/api/me")

@router.get("/plans")
def get_plans():
    return service.get_plans()

@router.get("/bookmark/place")
def get_bookmark_place():
    return service.get_bookmark_place()

@router.get("/like/board")
def get_bookmark_plans():
    return service.get_bookmark_plans()