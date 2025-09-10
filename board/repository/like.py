import uuid
from user.repository import get_connection

con, cur = get_connection()

def like_board(plan_id: uuid.UUID, user_id: uuid.UUID):
    # cur.execute("""
    #
    # """
    return None

def delete_like_board(plan_id: uuid.UUID, user_id: uuid.UUID):
    return None