import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        con = psycopg2.connect(database_url)
    else:
        con = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            dbname=os.getenv('DB_NAME', 'nomadly'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            port=int(os.getenv('DB_PORT', '5432'))
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
    try:
        create_table_if_not_exists("user", user_table_sql)
        create_table_if_not_exists("interest", interest_table_sql)
        print("✅ Database tables initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        # Don't crash the app, just log the error

# Only initialize tables if we're not in import-only mode
if __name__ != '__main__':
    try:
        create_all_tables()
    except Exception as e:
        print(f"⚠️ Database connection failed during startup: {e}")
        print("📝 App will continue without database initialization")