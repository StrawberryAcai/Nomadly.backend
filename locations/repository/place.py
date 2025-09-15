import uuid
from typing import Optional, List, Dict, Any
from locations.repository import get_connection

class PlaceRepository:
    def create_place(self, *, place_id: uuid.UUID, name: str, address: Optional[str] = None) -> Dict[str, Any]:
        sql = """
        INSERT INTO place (place_id, name, address)
        VALUES (%s, %s, %s)
        RETURNING place_id, name, address, overall_rating, overall_bookmark;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(place_id), name, address))
            row = cur.fetchone()
            con.commit()
            return row
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    def get_place(self, place_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT place_id, name, address, overall_rating, overall_bookmark
        FROM place WHERE place_id = %s;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(place_id),))
            return cur.fetchone()
        finally:
            cur.close()
            con.close()

    def get_place_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        이름으로 장소를 검색합니다.
        """
        sql = """
        SELECT place_id, name, address, overall_rating, overall_bookmark
        FROM place WHERE name = %s;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (name,))
            return cur.fetchone()
        finally:
            cur.close()
            con.close()

    def get_place_by_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        주소로 장소를 검색합니다. 완전 일치 기준.
        """
        sql = """
        SELECT place_id, name, address, overall_rating, overall_bookmark
        FROM place WHERE address = %s
        LIMIT 1;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (address,))
            return cur.fetchone()
        finally:
            cur.close()
            con.close()

    def list_places(self, *, limit: int = 20, offset: int = 0, order_by: str = "overall_bookmark DESC") -> List[Dict[str, Any]]:
        allowed = {
            "name", "name DESC",
            "overall_rating", "overall_rating DESC",
            "overall_bookmark", "overall_bookmark DESC"
        }
        ob = order_by if order_by in allowed else "overall_bookmark DESC"
        sql = f"""
        SELECT place_id, name, address, overall_rating, overall_bookmark
        FROM place
        ORDER BY {ob}
        LIMIT %s OFFSET %s;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (limit, offset))
            return cur.fetchall()
        finally:
            cur.close()
            con.close()

    def update_place(self, *, place_id: uuid.UUID, name: Optional[str] = None, address: Optional[str] = None) -> Optional[Dict[str, Any]]:
        sets, params = [], []
        if name is not None:
            sets.append("name = %s")
            params.append(name)
        if address is not None:
            sets.append("address = %s")
            params.append(address)
        if not sets:
            return self.get_place(place_id)

        params.append(str(place_id))
        sql = f"""
        UPDATE place
        SET {", ".join(sets)}
        WHERE place_id = %s
        RETURNING place_id, name, address, overall_rating, overall_bookmark;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, tuple(params))
            row = cur.fetchone()
            con.commit()
            return row
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    def delete_place(self, place_id: uuid.UUID) -> bool:
        sql = "DELETE FROM place WHERE place_id = %s;"
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(place_id),))
            deleted = cur.rowcount > 0
            con.commit()
            return deleted
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    def refresh_aggregates(self, place_id: uuid.UUID) -> Dict[str, Any]:
        """
        overall_bookmark = place_bookmark 카운트
        overall_rating   = rating 평균(소수1자리), 없으면 0
        """
        sql = """
        WITH b AS (
          SELECT COUNT(*)::bigint AS cnt
          FROM place_bookmark
          WHERE place_id = %s
        ),
        r AS (
          SELECT COALESCE(ROUND(AVG(score)::numeric, 1), 0)::numeric(2,1) AS avg_score
          FROM rating
          WHERE place_id = %s
        )
        UPDATE place
        SET overall_bookmark = (SELECT cnt FROM b),
            overall_rating   = (SELECT avg_score FROM r)
        WHERE place_id = %s
        RETURNING place_id, name, address, overall_rating, overall_bookmark;
        """
        pid = str(place_id)
        con, cur = get_connection()
        try:
            cur.execute(sql, (pid, pid, pid))
            row = cur.fetchone()
            con.commit()
            return row
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()