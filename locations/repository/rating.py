import uuid
from typing import List, Dict, Any
from locations.repository import get_connection
from locations.repository.place import PlaceRepository

class RatingRepository:
    def __init__(self):
        self.places = PlaceRepository()

    def upsert_rating(self, *, rating_id: uuid.UUID, user_id: uuid.UUID, place_id: uuid.UUID, score: int) -> Dict[str, Any]:
        sql = """
        INSERT INTO rating (rating_id, user_id, place_id, score)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, place_id)
        DO UPDATE SET score = EXCLUDED.score
        RETURNING rating_id, user_id, place_id, score;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(rating_id), str(user_id), str(place_id), score))
            row = cur.fetchone()
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

        refreshed = self.places.refresh_aggregates(place_id)
        return {"rating": row, "place": refreshed}

    def delete_rating(self, *, user_id: uuid.UUID, place_id: uuid.UUID) -> Dict[str, Any]:
        sql = "DELETE FROM rating WHERE user_id = %s AND place_id = %s;"
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

    def list_place_ratings(self, place_id: uuid.UUID, *, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        sql = """
        SELECT rating_id, user_id, place_id, score
        FROM rating
        WHERE place_id = %s
        ORDER BY rating_id
        LIMIT %s OFFSET %s;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(place_id), limit, offset))
            return cur.fetchall()
        finally:
            cur.close()
            con.close()
