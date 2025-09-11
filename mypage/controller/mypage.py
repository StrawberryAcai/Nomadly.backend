from fastapi import APIRouter

router = APIRouter(prefix="/api/me")

@router.get("/plans")
def get_plans():
    return None

@router.get("/bookmark/place")

@router.get("/like/board")
def get_bookmark_plans():
    return None