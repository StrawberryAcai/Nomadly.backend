from user.entity.interest import Interest
import uuid

from user.repository import get_connection

def create_interest(user_id: uuid.UUID, interest: str) -> int:
    con, cur = get_connection()
    try:
        cur.execute(
            "INSERT INTO interest (user_id, interest) VALUES (%s, %s) RETURNING id",
            (str(user_id), interest)
        )
        interest_id = cur.fetchone()[0]
        con.commit()
        return interest_id
    finally:
        cur.close()
        con.close()

def get_interest(interest_id: int) -> Interest | None:
    con, cur = get_connection()
    try:
        cur.execute(
            "SELECT id, user_id, interest FROM interest WHERE id = %s",
            (interest_id,)
        )
        row = cur.fetchone()
        if row:
            return Interest(id=row[0], user_id=uuid.UUID(row[1]), interest=row[2])
        return None
    finally:
        cur.close()
        con.close()

def update_interest(interest_id: int, user_id: uuid.UUID, interest: str) -> int:
    con, cur = get_connection()
    try:
        cur.execute(
            "UPDATE interest SET user_id = %s, interest = %s WHERE id = %s",
            (str(user_id), interest, interest_id)
        )
        con.commit()
        return cur.rowcount
    finally:
        cur.close()
        con.close()

def delete_interest(interest_id: int) -> int:
    con, cur = get_connection()
    try:
        cur.execute(
            "DELETE FROM interest WHERE id = %s",
            (interest_id,)
        )
        con.commit()
        return cur.rowcount
    finally:
        cur.close()
        con.close()

def list_interests() -> list[Interest]:
    con, cur = get_connection()
    try:
        cur.execute("SELECT id, user_id, interest FROM interest")
        rows = cur.fetchall()
        return [Interest(id=row[0], user_id=uuid.UUID(row[1]), interest=row[2]) for row in rows]
    finally:
        cur.close()
        con.close()

def get_interests_by_user_id(user_id: uuid.UUID) -> list[Interest]:
    con, cur = get_connection()
    try:
        cur.execute(
            "SELECT id, user_id, interest FROM interest WHERE user_id = %s",
            (str(user_id),)
        )
        rows = cur.fetchall()
        return [Interest(id=row[0], user_id=uuid.UUID(row[1]), interest=row[2]) for row in rows]
    finally:
        cur.close()
        con.close()