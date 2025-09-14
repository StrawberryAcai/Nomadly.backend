import uuid
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Query, Path

from board.model.document import BoardResponse, BoardDetailResponse
from board.service import document as service
from user.controller.user import get_current_user_id

router = APIRouter(prefix="/api/board")

@router.get("", response_model=List[BoardResponse])
def get_all_boards(
        keyword: Optional[str] = Query(None),
        user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    return service.get_all_boards(keyword, user_id)

@router.get("/{board_id}", response_model=BoardDetailResponse)
def get_board_details(
        board_id: str,
        user_id: uuid.UUID = Depends(get_current_user_id)
    ):
    board_id = uuid.UUID(board_id)
    return service.get_board_details(board_id, user_id)