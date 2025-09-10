import uuid

from board.repository import like as repository


def like_board(plan_id: uuid.UUID, user_id: uuid.UUID):
    return repository.like_board(plan_id, user_id)


def delete_like_board(plan_id: uuid.UUID, user_id: uuid.UUID):
    return repository.delete_like_board(plan_id, user_id)