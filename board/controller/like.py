import uuid

from board.service import like as service
from fastapi import APIRouter, Body, Depends

from user.controller.user import get_current_user_id

router = APIRouter(prefix="/api/board/like")

@router.post("")
def like_board(
        request: dict = Body(...),
        user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    board_id = request["board_id"]
    return service.like_board(board_id, user_id)

@router.delete("")
def delete_like_board(
        request: dict = Body(...)
        , user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    board_id = request["board_id"]
    return service.delete_like_board(board_id, user_id)