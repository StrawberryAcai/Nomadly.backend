from __future__ import annotations
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from user.repository import get_connection


class PlanRepository:
    def create_plan(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        private: bool = True,
        author: Optional[UUID] = None,
    ) -> UUID:
        """
        plan 레코드 생성 후 plan_id 반환.
        - start_date/end_date: UTC naive TIMESTAMP로 저장
        - author: 소유 사용자 id (nullable)
        """
        plan_id = uuid4()
        con, cur = get_connection()
        try:
            cur.execute(
                "INSERT INTO plan (id, start_date, end_date, private, author) VALUES (%s, %s, %s, %s, %s);",
                (str(plan_id), start_date, end_date, bool(private), str(author) if author else None),
            )
            con.commit()
            return plan_id
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    def bulk_insert_items(self, *, plan_id: UUID, items: List[Dict[str, Any]]) -> None:
        """
        items: [{todo:str, place:str, time: datetime}, ...]
        - time: UTC naive TIMESTAMP
        """
        if not items:
            return
        con, cur = get_connection()
        try:
            params = []
            for it in items:
                iid = str(uuid4())
                todo = str(it.get("todo", "") or "")
                place = str(it.get("place", "") or "")
                t: Optional[datetime] = it.get("time")  # type: ignore[name-defined]
                params.append((iid, str(plan_id), todo, place, t))
            cur.executemany(
                "INSERT INTO plan_item (id, plan_id, todo, place, time) VALUES (%s, %s, %s, %s, %s);",
                params,
            )
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    def get_plan_by_id(self, plan_id: UUID) -> Optional[Dict[str, Any]]:
        """plan_id로 plan 조회"""
        sql = "SELECT id, start_date, end_date, private, author FROM plan WHERE id = %s;"
        con, cur = get_connection()
        try:
            cur.execute(sql, (str(plan_id),))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "start_date": row[1],
                "end_date": row[2],
                "private": row[3],
                "author": row[4]
            }
        finally:
            cur.close()
            con.close()

    def update_plan_visibility(self, *, plan_id: UUID, private: bool) -> bool:
        """plan의 공개 여부(private) 변경"""
        sql = "UPDATE plan SET private = %s WHERE id = %s;"
        con, cur = get_connection()
        try:
            cur.execute(sql, (bool(private), str(plan_id)))
            updated = cur.rowcount > 0
            con.commit()
            return updated
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()
