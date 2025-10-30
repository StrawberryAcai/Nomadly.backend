import uuid
from user.repository import get_connection

def like_board(board_id: uuid.UUID, user_id: uuid.UUID):
    con, cur = get_connection()
    try:
        cur.execute("""
        insert into public."like" (id, user_id, board_id)
            values (%s, %s, %s);
        """, (str(uuid.uuid4()), str(user_id), str(board_id))
        )
        con.commit()

        cur.execute("""
            UPDATE board 
            SET likes = COALESCE((
                SELECT COUNT(*) 
                FROM "like" l 
                WHERE l.board_id = board.id
            ), 0)
            WHERE id IS NOT NULL;
        """)
        con.commit()
    finally:
        cur.close()
        con.close()

def delete_like_board(board_id: uuid.UUID, user_id: uuid.UUID):
    con, cur = get_connection()
    try:
        cur.execute("""
        delete from public."like"
        where board_id = %s and user_id = %s;
        """, (str(board_id), str(user_id)))
        con.commit()

        cur.execute("""
        update board
        set likes= likes - 1
            where id = %s;
        """, (str(board_id),))
        con.commit()
    finally:
        cur.close()
        con.close()