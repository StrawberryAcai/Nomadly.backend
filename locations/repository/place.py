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
            norm_name = (name or "").strip()
            norm_addr = (address or None)
            if norm_addr is not None:
                norm_addr = norm_addr.strip() or None
            cur.execute(sql, (str(place_id), norm_name, norm_addr))
            row = cur.fetchone()
            con.commit()
            if not row:
                return {"place_id": str(place_id), "name": norm_name, "address": norm_addr, "overall_rating": 0.0, "overall_bookmark": 0}
            return {
                "place_id": row[0],
                "name": row[1],
                "address": row[2],
                "overall_rating": row[3],
                "overall_bookmark": row[4],
            }
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
            row = cur.fetchone()
            if not row:
                return None
            return {
                "place_id": row[0],
                "name": row[1],
                "address": row[2],
                "overall_rating": row[3],
                "overall_bookmark": row[4],
            }
        finally:
            cur.close()
            con.close()

    def get_place_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        이름으로 장소를 검색합니다.
        """
        sql = """
        SELECT place_id, name, address, overall_rating, overall_bookmark
        FROM place WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
        LIMIT 1;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (name.strip(),))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "place_id": row[0],
                "name": row[1],
                "address": row[2],
                "overall_rating": row[3],
                "overall_bookmark": row[4],
            }
        finally:
            cur.close()
            con.close()

    def get_place_by_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        주소로 장소를 검색합니다. 완전 일치 기준.
        """
        sql = """
        SELECT place_id, name, address, overall_rating, overall_bookmark
        FROM place WHERE LOWER(TRIM(address)) = LOWER(TRIM(%s))
        LIMIT 1;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (address.strip(),))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "place_id": row[0],
                "name": row[1],
                "address": row[2],
                "overall_rating": row[3],
                "overall_bookmark": row[4],
            }
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
            rows = cur.fetchall()
            return [
                {
                    "place_id": r[0],
                    "name": r[1],
                    "address": r[2],
                    "overall_rating": r[3],
                    "overall_bookmark": r[4],
                }
                for r in rows
            ]
        finally:
            cur.close()
            con.close()

    def update_place(self, *, place_id: uuid.UUID, name: Optional[str] = None, address: Optional[str] = None) -> Optional[Dict[str, Any]]:
        sets: List[str] = []
        params: List[Any] = []
        if name is not None:
            sets.append("name = %s")
            params.append(name.strip())
        if address is not None:
            sets.append("address = %s")
            params.append(address.strip())
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
            if not row:
                return None
            return {
                "place_id": row[0],
                "name": row[1],
                "address": row[2],
                "overall_rating": row[3],
                "overall_bookmark": row[4],
            }
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
        """place.overall_bookmark를 실제 북마크 수로 갱신하고 최신 레코드를 반환"""
        sql = """
        UPDATE place p
        SET overall_bookmark = (
            SELECT COUNT(*) FROM place_bookmark b WHERE b.place_id = p.place_id
        )
        WHERE p.place_id = %s
        RETURNING place_id, name, address, overall_rating, overall_bookmark;
        """
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(place_id),))
            row = cur.fetchone()
            con.commit()
            if not row:
                return self.get_place(place_id) or {
                    "place_id": str(place_id),
                    "name": "",
                    "address": None,
                    "overall_rating": 0.0,
                    "overall_bookmark": 0,
                }
            return {
                "place_id": row[0],
                "name": row[1],
                "address": row[2],
                "overall_rating": row[3],
                "overall_bookmark": row[4],
            }
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()