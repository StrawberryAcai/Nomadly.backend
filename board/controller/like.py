import uuid

from board.service import like as service
from fastapi import APIRouter, Body

router = APIRouter(prefix="/api/board/like")

@router.post("")
def like_board(
        plan_id: uuid.UUID = Body(...)
        # ,user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    user_id = uuid.UUID("6ee53234-1dc5-44e8-8f3c-b2b98530aca6")
    return service.like_board(plan_id, user_id)

@router.delete("")
def delete_like_board(
        plan_id: uuid.UUID = Body(...)
        # ,user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    user_id = uuid.UUID("6ee53234-1dc5-44e8-8f3c-b2b98530aca6")
    return service.delete_like_board(plan_id, user_id)