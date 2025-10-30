import uuid

from user.repository import get_connection

def get_plans(user_id: uuid.UUID):
    con, cur = get_connection()
    try:
        cur.execute(
            """
            select 
                p.id, p.start_date, p.end_date,
                i.todo, i.place, i."time"
            from plan p join plan_item i
            on p.id = i.plan_id
            where p.author = %s;
            """, (str(user_id),)
        )
        return cur.fetchall()
    finally:
        cur.close()
        con.close()

def get_bookmark_place(user_id: uuid.UUID):
    con, cur = get_connection()
    try:
        cur.execute(
            """
            select 
                p.place_id, p."name", p.address,
                p.overall_bookmark, p.overall_rating
            from place p join place_bookmark b
            on p.place_id = b.place_id
            where b.user_id = %s;
            """, (str(user_id),)
        )
        return cur.fetchall()
    finally:
        cur.close()
        con.close()


def get_like_boards(user_id: uuid.UUID):
    con, cur = get_connection()
    try:
        cur.execute(
            """
            select 
                b.plan_id, b.title, b.content, b.likes
            from board b join "like" l
            on b.id = l.board_id and l.user_id = %s;
            """, (str(user_id),)
        )
        return cur.fetchall()
    finally:
        cur.close()
        con.close()