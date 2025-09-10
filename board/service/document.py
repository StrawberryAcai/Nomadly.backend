import uuid
from typing import Optional, List

from board.model.document import BoardResponse

from board.repository import document as repository

def rows_to_board_response(rows) -> List[BoardResponse]:
    results = []
    for row in rows:
        results.append({
            "board_id": row[0],
            "title": row[1],
            "content": row[2],
            "is_liked": row[3],
            "likes": row[4]
        })
    return results

def get_all_boards(keyword: Optional[str], user_id: uuid.UUID):
    if keyword is None:
        result = repository.get_all_boards(user_id)
    else:
        result = repository.get_all_boards_with_keyword(keyword, user_id)
    return rows_to_board_response(result)

def get_board_details(board_id: uuid.UUID, user_id: uuid.UUID):
    return repository.get_board_details(board_id, user_id)