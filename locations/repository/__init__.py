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

place_table_sql = """
CREATE TABLE IF NOT EXISTS place (
    place_id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    overall_rating DECIMAL(2,1) DEFAULT 0,
    overall_bookmark BIGINT DEFAULT 0
);
"""

bookmark_table_sql = """
CREATE TABLE IF NOT EXISTS bookmark (
    bookmark_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    place_id UUID NOT NULL,
    UNIQUE(user_id, place_id),
    FOREIGN KEY(user_id) REFERENCES user(user_id),
    FOREIGN KEY(place_id) REFERENCES place(place_id)
);
"""

rating_table_sql = """
CREATE TABLE IF NOT EXISTS rating (
    rating_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    place_id UUID NOT NULL,
    score INT CHECK(score >= 1 AND score <= 5),
    UNIQUE(user_id, place_id),
    FOREIGN KEY(user_id) REFERENCES user(user_id),
    FOREIGN KEY(place_id) REFERENCES place(place_id)
);
"""

def create_all_tables():
    create_table_if_not_exists("place", place_table_sql)
    create_table_if_not_exists("bookmark", bookmark_table_sql)
    create_table_if_not_exists("rating", interest_table_sql)

create_all_tables()