import uuid

from mypage.repository import mypage as repository


def get_plans(user_id: uuid.UUID):
    return repository.get_plans(user_id)


def get_bookmark_place(user_id: uuid.UUID):
    return repository.get_bookmark_place(user_id)


def get_like_plans(user_id: uuid.UUID):
    return repository.get_like_plans(user_id)