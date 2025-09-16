from user.repository import get_connection

def create_table_if_not_exists(table_name, create_sql):
    con, cur = get_connection()
    try:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            );
        """, (table_name,))
        exists = cur.fetchone()[0]
        if not exists:
            cur.execute(create_sql)
            con.commit()
    finally:
        cur.close()
        con.close()

# 새로 추가할 board, like, bookmark
board_table_sql = """
CREATE TABLE board (
    id UUID PRIMARY KEY,
    author UUID NOT NULL,
    likes INT DEFAULT 0,
    title TEXT NOT NULL,
    content TEXT,
    FOREIGN KEY (author) REFERENCES "user"(id)
);
"""

like_table_sql = """
CREATE TABLE "like" (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    board_id UUID NOT NULL,
    liked_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (board_id) REFERENCES board(id) ON DELETE CASCADE,
    UNIQUE (user_id, board_id)
);
"""

def create_all_tables():
    create_table_if_not_exists("board", board_table_sql)
    create_table_if_not_exists("like", like_table_sql)

create_all_tables()
