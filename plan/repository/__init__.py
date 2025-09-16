import psycopg2

import os
import psycopg2
from psycopg2.extensions import connection, cursor
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

plan_table_sql = """
CREATE TABLE IF NOT EXISTS public.plan (
    id UUID PRIMARY KEY,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    private boolean default true,
    author UUID REFERENCES "user"(id) ON DELETE SET NULL
);
"""

plan_item_table_sql = """
CREATE TABLE IF NOT EXISTS public.plan_item (
    id UUID PRIMARY KEY,
    plan_id UUID REFERENCES plan(id) ON DELETE CASCADE,
    todo VARCHAR(100) NOT NULL,
    place VARCHAR(100),
    time TIMESTAMP
);
"""

def create_all_tables():
    create_table_if_not_exists("plan", plan_table_sql)
    create_table_if_not_exists("plan_item", plan_item_table_sql)

create_all_tables()
