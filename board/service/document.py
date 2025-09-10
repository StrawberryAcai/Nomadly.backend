import uuid
from typing import Optional, List

from board.model.document import BoardResponse, BoardDetailResponse

from board.repository import document as repository

def get_all_boards(keyword: Optional[str], user_id: uuid.UUID) -> List[BoardResponse]:
    if keyword is None:
        rows = repository.get_all_boards(user_id)
    else:
        rows = repository.get_all_boards_with_keyword(keyword, user_id)
    result = []
    for row in rows:
        result.append(
            BoardResponse(
                board_id=row[0],
                title=row[1],
                content=row[2],
                is_liked=row[3],
                likes=row[4]
            )
        )
    return result

def get_board_details(board_id: uuid.UUID, user_id: uuid.UUID) -> BoardDetailResponse:
    board = repository.get_board_details(board_id, user_id)

    plan_id = uuid.UUID(board[-1])
    plan_rows = repository.get_plan_by_id(plan_id)
    plan = []
    start_time = plan_rows[0][1]
    end_time = plan_rows[0][2]
    for plan_row in plan_rows:
        plan.append(
            {
                "todo" : plan_row[3],
                "place" : plan_row[4],
                "time" : plan_row[5]
            }
        )

    return BoardDetailResponse(
        board_id=board_id,
        title=board[0],
        content=board[1],
        is_liked=board[2],
        likes=board[3],
        plan={
            "start_time" : start_time,
            "end_time" : end_time,
            "plan" : plan
        }
    )