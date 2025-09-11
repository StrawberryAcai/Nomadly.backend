import uuid

from user.repository import get_connection

cur, con = get_connection()

def get_plans(
        user_id: uuid.UUID
    ):
    return None


def get_bookmark_place(
        user_id: uuid.UUID
    ):
    return None


def get_bookmark_plans(
        user_id: uuid.UUID
    ):
    return None