from typing import Any, Dict, Optional
from uuid import uuid4
from urllib.parse import unquote
import re
from fastapi import HTTPException

from locations.repository.place import PlaceRepository
from locations.model.response.place import PlaceResponse

class PlaceService:
    def __init__(self) -> None:
        self.repo = PlaceRepository()

    def _normalize_name(self, raw: str) -> str:
        s = unquote(raw or "").strip()
        if len(s) >= 2 and s[0] in {'"', "'", '`'} and s[-1] == s[0]:
            s = s[1:-1]
        s = re.sub(r'[\x00-\x1F\x7F]', '', s)
        return s

    def _row_to_place_dict(self, row: Any) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        if isinstance(row, dict):
            return {
                "place_id": row.get("place_id"),
                "name": row.get("name"),
                "address": row.get("address"),
                "overall_rating": float(row.get("overall_rating", 0.0) or 0.0),
                "overall_bookmark": int(row.get("overall_bookmark", 0) or 0),
            }
        try:
            # (place_id, name, address, overall_rating, overall_bookmark)
            return {
                "place_id": row[0],
                "name": row[1],
                "address": row[2],
                "overall_rating": float(row[3] or 0.0),
                "overall_bookmark": int(row[4] or 0),
            }
        except Exception:
            return None

    def get_or_create_place(self, place_name: str) -> PlaceResponse:
        norm_name = self._normalize_name(place_name)
        if not norm_name:
            raise HTTPException(status_code=400, detail="유효하지 않은 장소 이름입니다.")

        row = self.repo.get_place_by_name(norm_name)
        place_dict = self._row_to_place_dict(row)
        if place_dict:
            return PlaceResponse(**place_dict)

        try:
            new_place_id = uuid4()
            created_row = self.repo.create_place(place_id=new_place_id, name=norm_name, address=None)
            created_dict = self._row_to_place_dict(created_row)
            if not created_dict:
                raise HTTPException(status_code=500, detail="장소 생성 결과를 해석할 수 없습니다.")
            return PlaceResponse(**created_dict)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"장소 생성 중 오류: {str(e)}")
