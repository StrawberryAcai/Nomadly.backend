import uuid

from fastapi import Body

from board.repository import like as repository


def like_board(
        board_id: uuid.UUID,
        user_id: uuid.UUID):
    repository.like_board(board_id, user_id)
    return {
        "msg" : "좋아요를 성공적으로 완료함"
    }


def delete_like_board(
        board_id: uuid.UUID,
        user_id: uuid.UUID):
    repository.delete_like_board(board_id, user_id)
    return {
        "msg" : "좋아요를 성공적으로 취소함"
    }