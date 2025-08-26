import uuid
from user.entity.user import User
from user.repository import get_connection

con, cur = get_connection()

def create_user(profile, username, password):
    user_id = uuid.uuid4()
    cur.execute(
        "INSERT INTO \"user\" (id, profile, username, password) VALUES (%s, %s, %s, %s)",
        (str(user_id), username, profile, password)
    )
    con.commit()
    return user_id

def get_user(user_id):
    cur.execute(
        "SELECT id, profile, username, password FROM \"user\" WHERE id = %s",
        (str(user_id),)
    )
    row = cur.fetchone()
    if row:
        return User(id=uuid.UUID(row[0]), profile=row[1], username=row[2], password=row[3])
    return None

def update_user_profile(user_id, profile):
    cur.execute(
        "UPDATE \"user\" SET profile = %s WHERE id = %s",
        (profile, str(user_id))
    )
    con.commit()
    return cur.rowcount

def update_user_password(user_id, password):
    cur.execute(
        "UPDATE \"user\" SET password = %s WHERE id = %s",
        (password, str(user_id))
    )
    con.commit()
    return cur.rowcount

def update_user_username(user_id, username):
    cur.execute(
        "UPDATE \"user\" SET username = %s WHERE id = %s",
        (username, str(user_id))
    )
    con.commit()
    return cur.rowcount

def delete_user(user_id):
    cur.execute(
        "DELETE FROM \"user\" WHERE id = %s",
        (str(user_id),)
    )
    con.commit()
    return cur.rowcount

def list_users():
    cur.execute("SELECT id, profile, username, password FROM \"user\"")
    rows = cur.fetchall()
    return [User(id=uuid.UUID(row[0]), profile=row[1], username=row[2], password=row[3]) for row in rows]

def get_user_by_username(username):
    cur.execute(
        "SELECT id, profile, username, password FROM \"user\" WHERE username = %s",
        (str(username),)
    )
    row = cur.fetchone()
    if row:
        return User(id=uuid.UUID(row[0]), profile=row[1], username=row[2], password=row[3])
    return None

def get_password_by_username(username):
    cur.execute(
        "SELECT password FROM \"user\" WHERE username = %s",
        (str(username),)
    )
    row = cur.fetchone()
    if row:
        return row[0]
    return None