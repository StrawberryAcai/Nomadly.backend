import uuid
from user.repository import get_connection

con, cur = get_connection()

def get_all_boards_with_keyword(keyword: str, user_id: uuid.UUID):
    cur.execute(
        """
        SELECT b.id, b.title, b.content, l.id is not null AS is_liked, b.likes
        FROM public.board b
        LEFT JOIN public."like" l
        ON b.id = l.board_id AND l.user_id = %s
        WHERE b.title ILIKE %s;
        """,
        (str(user_id), f'%{keyword}%')
    )
    return cur.fetchall()

def get_all_boards(user_id: uuid.UUID):
    cur.execute(
        """
        SELECT b.title, b.content, l.id is not null AS is_liked, b.likes
        FROM public.board b
        LEFT JOIN public."like" l
        ON b.id = l.board_id AND l.user_id = %s;
        """,
        (str(user_id))
    )

    return cur.fetchall()

def get_board_details(board_id: uuid.UUID, user_id: uuid.UUID):
    return None