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

user_table_sql = """
CREATE TABLE IF NOT EXISTS "user" (
    id UUID PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    profile TEXT NOT NULL,
    password TEXT NOT NULL
);
"""

interest_table_sql = """
CREATE TABLE IF NOT EXISTS interest (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    interest TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);
"""

def create_all_tables():
    create_table_if_not_exists("user", user_table_sql)
    create_table_if_not_exists("interest", interest_table_sql)

create_all_tables()