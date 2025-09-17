import uuid
from typing import List, Dict, Any
from locations.repository import get_connection
from locations.repository.place import PlaceRepository

class BookmarkRepository:
    def __init__(self):
        self.places = PlaceRepository()

    def add_bookmark(self, *, bookmark_id: uuid.UUID, user_id: uuid.UUID, place_id: uuid.UUID) -> Dict[str, Any]:
        sql = """
        INSERT INTO place_bookmark (bookmark_id, user_id, place_id)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, place_id) DO NOTHING
        RETURNING bookmark_id, user_id, place_id;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(bookmark_id), str(user_id), str(place_id)))
            row = cur.fetchone()  # None이면 이미 존재했던 것
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

        refreshed = self.places.refresh_aggregates(place_id)
        return {"bookmark": row, "place": refreshed}

    def remove_bookmark(self, *, user_id: uuid.UUID, place_id: uuid.UUID) -> Dict[str, Any]:
        sql = "DELETE FROM place_bookmark WHERE user_id = %s AND place_id = %s;"
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(user_id), str(place_id)))
            deleted = cur.rowcount > 0
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

        refreshed = self.places.refresh_aggregates(place_id)
        return {"deleted": deleted, "place": refreshed}

    def list_user_bookmarks(self, user_id: uuid.UUID, *, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        sql = """
        SELECT b.bookmark_id, b.user_id, b.place_id,
               p.name, p.address, p.overall_rating, p.overall_bookmark
        FROM place_bookmark b
        JOIN place p ON p.place_id = b.place_id
        WHERE b.user_id = %s
        ORDER BY p.overall_bookmark DESC
        LIMIT %s OFFSET %s;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(user_id), limit, offset))
            return cur.fetchall()
        finally:
            cur.close()
            con.close()

    # 새 메서드: 특정 사용자/장소 북마크 존재 여부
    def has_bookmark(self, *, user_id: uuid.UUID, place_id: uuid.UUID) -> bool:
        sql = "SELECT EXISTS (SELECT 1 FROM place_bookmark WHERE user_id = %s AND place_id = %s);"
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(user_id), str(place_id)))
            row = cur.fetchone()
            return bool(row and row[0])
        finally:
            cur.close()
            con.close()
