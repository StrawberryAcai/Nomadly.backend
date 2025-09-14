from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from locations.repository import get_connection
from locations.repository.place import PlaceRepository

class RatingRepository:
    def add_rating(self, *, place_id: UUID, score: float, user_id: UUID) -> None:
        """
        rating_id와 user_id를 포함해 저장합니다. score는 0.0~5.0 범위로 클램프.
        """
        s = max(0.0, min(5.0, float(score)))
        rid = str(uuid4())
        sql = "INSERT INTO rating (rating_id, user_id, place_id, score) VALUES (%s, %s, %s, %s);"
        params = (rid, str(user_id), str(place_id), s)

        con, cur = get_connection()
        try:
            cur.execute(sql, params)
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

        # place 집계 즉시 갱신 (트리거가 있다면 중복이어도 문제 없음)
        try:
            PlaceRepository().refresh_aggregates(place_id)
        except Exception:
            pass

    def get_rating_by_place_id(self, place_id: UUID) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT
            COALESCE(ROUND(AVG(score)::numeric, 1), 0)::float8 AS average_rating,
            COUNT(*)::bigint AS total_ratings
        FROM rating
        WHERE place_id = %s;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(place_id),))
            row = cur.fetchone()
            if not row:
                return None
            avg = float(row[0] or 0.0)
            cnt = int(row[1] or 0)
            return {"place_id": place_id, "average_rating": avg, "total_ratings": cnt}
        finally:
            cur.close()
            con.close()

    def refresh_rating_aggregates(self, place_id: UUID) -> Dict[str, Any]:
        sql = """
        SELECT
            COALESCE(ROUND(AVG(score)::numeric, 1), 0)::float8 AS average_rating,
            COUNT(*)::bigint AS total_ratings
        FROM rating
        WHERE place_id = %s;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(place_id),))
            row = cur.fetchone()
            avg = float(row[0] or 0.0)
            cnt = int(row[1] or 0)
        finally:
            cur.close()
            con.close()

        try:
            PlaceRepository().refresh_aggregates(place_id)
        except Exception:
            pass

        return {"place_id": place_id, "average_rating": avg, "total_ratings": cnt}