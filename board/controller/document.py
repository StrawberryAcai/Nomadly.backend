import uuid
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Query, Path

from board.model.document import BoardResponse
from board.service import document as service
from user.controller.user import get_current_user_id

router = APIRouter(prefix="/api/board")

@router.get("", response_model=List[BoardResponse])
def get_all_boards(
        keyword: Optional[str] = Query(None)
        # ,user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    user_id = uuid.UUID("97e9c973-62fb-422a-bf24-79e2b39ace21")
    return service.get_all_boards(keyword, user_id)

@router.get("/{plan_id}")
def get_board_details(
        plan_id: uuid.UUID = Path(...)
        # , user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    user_id = uuid.UUID("97e9c973-62fb-422a-bf24-79e2b39ace21")
    return service.get_board_details(plan_id, user_id)