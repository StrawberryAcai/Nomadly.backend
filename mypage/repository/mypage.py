import uuid

from user.repository import get_connection

cur, con = get_connection()

def get_plans(user_id: uuid.UUID):
    cur.execute(
        """
        select 
            p.id, p.start_date, p.end_date,
            p.private, i.todo, i.place, i."time"
        from plan p join plan_item i
        on p.id = i.plan_id
        where p.author = %s;
        """, (user_id,)
    )
    return con.fetchall()


def get_bookmark_place(user_id: uuid.UUID):
    cur.execute(
        """
        select 
            p.place_id, p."name", p.address,
            p.overall_bookmark, p.overall_rating
        from place p join place_bookmark b
        on p.place_id = b.place_id
        where b.user_id = %s;
        """, (user_id,)
    )
    return con.fetchall()


def get_like_boards(user_id: uuid.UUID):
    cur.execute(
        """
        select 
            b.plan_id, b.title, b.content, b.likes
        from board b join "like" l
        on b.id = l.board_id
        where b.author = %s;
        """, (user_id,)
    )
    return con.fetchall()