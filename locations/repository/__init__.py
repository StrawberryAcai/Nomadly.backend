import psycopg2

import os
import psycopg2
from psycopg2.extensions import connection, cursor

def get_connection() -> tuple[connection, cursor]:
    """
    Supabase PostgreSQL 데이터베이스에 연결합니다.
    """
    con = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        port=os.getenv("DB_PORT", 5432)
    )
    cur = con.cursor()
    return con, cur

# ...existing code...
import psycopg2

def apply_rating_trigger_migration() -> None:
    """
    rating 변경 시 place.overall_rating 자동 갱신 트리거/함수 생성 (idempotent)
    """
    fn_sql = """
    CREATE OR REPLACE FUNCTION refresh_place_overall_rating() RETURNS TRIGGER AS $$
    DECLARE
      affected uuid;
    BEGIN
      affected := COALESCE(NEW.place_id, OLD.place_id);
      UPDATE place p
      SET overall_rating = (
          SELECT COALESCE(ROUND(AVG(r.score)::numeric, 1), 0)::numeric(2,1)
          FROM rating r
          WHERE r.place_id = p.place_id
      )
      WHERE p.place_id = affected;
      RETURN COALESCE(NEW, OLD);
    END;
    $$ LANGUAGE plpgsql;
    """
    trg_sql = """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_rating_refresh_place'
      ) THEN
        CREATE TRIGGER trg_rating_refresh_place
        AFTER INSERT OR UPDATE OR DELETE ON rating
        FOR EACH ROW
        EXECUTE PROCEDURE refresh_place_overall_rating();
      END IF;
    END$$;
    """
    con, cur = get_connection()
    try:
        cur.execute(fn_sql)
        cur.execute(trg_sql)
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        cur.close()
        con.close()


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
CREATE TABLE IF NOT EXISTS place_bookmark (
    bookmark_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    place_id UUID NOT NULL,
    UNIQUE(user_id, place_id),
    FOREIGN KEY(user_id) REFERENCES "user"(id),
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
    FOREIGN KEY(user_id) REFERENCES "user"(id),
    FOREIGN KEY(place_id) REFERENCES place(place_id)
);
"""

def create_all_tables():
    create_table_if_not_exists("place", place_table_sql)
    create_table_if_not_exists("place_bookmark", bookmark_table_sql)
    create_table_if_not_exists("rating", rating_table_sql)

create_all_tables()