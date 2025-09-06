import psycopg2

def get_connection():
    con = psycopg2.connect(
        host='localhost',
        dbname='nomadly',
        user='postgres',
        password='postgres',
        port=5432
    )
    cur = con.cursor()
    return con, cur

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
CREATE TABLE IF NOT EXISTS board (
    id SERIAL PRIMARY KEY,
    author UUID NOT NULL,
    likes INT DEFAULT 0,
    title TEXT NOT NULL,
    content TEXT,
    FOREIGN KEY (author) REFERENCES "user"(id) ON DELETE CASCADE
);
"""

like_table_sql = """
CREATE TABLE IF NOT EXISTS "like" (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    board_id INT NOT NULL,
    liked_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (board_id) REFERENCES board(id) ON DELETE CASCADE,
    UNIQUE (user_id, board_id)
);
"""

bookmark_table_sql = """
CREATE TABLE IF NOT EXISTS bookmark (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    index INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);
"""

def create_all_tables():
    create_table_if_not_exists("board", board_table_sql)
    create_table_if_not_exists("like", like_table_sql)
    create_table_if_not_exists("bookmark", bookmark_table_sql)

create_all_tables()
