from typing import Any, Dict, Optional
from uuid import uuid4
from urllib.parse import unquote
import re
from fastapi import HTTPException
import os
from httpx import AsyncClient  # Kakao Local REST 호출용
from haversine import haversine  # 거리 계산

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
                "image": row.get("image") or row.get("image_url"),
                "distance": row.get("distance") or row.get("distance_meters"),
                "trend": row.get("trend"),
            }
        try:
            data = {
                "place_id": row[0],
                "name": row[1],
                "address": row[2],
                "overall_rating": float(row[3] or 0.0),
                "overall_bookmark": int(row[4] or 0),
            }
            if len(row) > 5:
                data["image"] = row[5]
            if len(row) > 6:
                data["distance"] = row[6]
            if len(row) > 7:
                data["trend"] = row[7]
            return data
        except Exception:
            return None

    async def _fetch_from_kakao(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        Kakao Local 검색 API(키워드)로 장소를 조회합니다.
        이미지는 제공되지 않으므로 빈 문자열을 반환합니다.
        """
        api_key = os.getenv("KAKAO_REST_API_KEY")
        if not api_key or not keyword.strip():
            return None

        headers = {"Authorization": f"KakaoAK {api_key}"}
        params = {"query": keyword, "size": 1, "page": 1}

        try:
            async with AsyncClient(timeout=10.0) as client:
                r = await client.get("https://dapi.kakao.com/v2/local/search/keyword.json",
                                     params=params, headers=headers)
                r.raise_for_status()
                data = r.json()
        except Exception:
            return None

        docs = data.get("documents") or []
        if not docs:
            return None

        first = docs[0]
        title = (first.get("place_name") or keyword).strip()
        address = (first.get("road_address_name") or first.get("address_name") or "").strip()
        # Kakao 좌표: x=경도, y=위도
        try:
            x = float(first.get("x")) if first.get("x") is not None else None
            y = float(first.get("y")) if first.get("y") is not None else None
        except Exception:
            x, y = None, None

        return {
            "name": title,
            "address": address,
            "image": "",              # Kakao Local은 이미지 미제공
            "overall_rating": 0.0,
            "overall_bookmark": 0,
            "trend": False,
            "distance": 0,
            "longitude": x,
            "latitude": y,
        }

    async def _fetch_image_from_tourapi(self, keyword: str) -> str:
        """
        TourAPI 검색으로 대표 이미지(firstimage/firstimage2)를 조회합니다.
        실패 시 공백 문자열 반환.
        """
        api_key = os.getenv("TOURAPI_KEY")
        if not api_key or not keyword.strip():
            return ""
        base = "http://apis.data.go.kr/B551011/KorService2/searchKeyword2"
        params = {
            "serviceKey": api_key,
            "_type": "json",
            "MobileOS": "ETC",
            "MobileApp": "Nomadly",
            "keyword": keyword,
            "numOfRows": 1,
            "pageNo": 1,
            "arrange": "Q",
        }
        try:
            async with AsyncClient(timeout=10.0) as client:
                r = await client.get(base, params=params)
                r.raise_for_status()
                data = r.json()
            items = (
                data.get("response", {})
                    .get("body", {})
                    .get("items", {})
                    .get("item", [])
            )
            if not isinstance(items, list):
                items = [items] if items else []
            if not items:
                return ""
            first = items[0] or {}
            img = (first.get("firstimage") or first.get("firstimage2") or "").strip()
            return img
        except Exception:
            return ""

    def _compute_distance_m(self, origin_lon: float, origin_lat: float, dest_lon: float, dest_lat: float) -> int:
        """
        경위도(경도, 위도)로부터 거리(m)를 정수로 반환
        """
        try:
            meters = haversine((origin_lat, origin_lon), (dest_lat, dest_lon), unit="m")
            return int(round(float(meters)))
        except Exception:
            return 0

    def _to_response_payload(self, place_dict: Dict[str, Any], fallback_name: str, place_id: Optional[str] = None, distance_override: Optional[int] = None) -> Dict[str, Any]:
        img = place_dict.get("image") or place_dict.get("image_url")
        img = img.strip() if isinstance(img, str) else ""
        address = (place_dict.get("address") or "").strip()

        # trend: bool, distance: int로 강제
        trend_bool = bool(place_dict.get("trend"))
        try:
            distance_int = int(float(place_dict.get("distance") or 0))
        except Exception:
            distance_int = 0
        if isinstance(distance_override, int):
            distance_int = max(0, distance_override)

        resolved_id = place_dict.get("place_id") or place_id or str(uuid4())

        return {
            # PlaceResponse 스키마에 맞는 필드만 반환
            "place_id": resolved_id,
            "place_name": place_dict.get("name") or fallback_name,
            "rating": float(place_dict.get("overall_rating") or 0.0),
            "trend": trend_bool,
            "bookmark_cnt": int(place_dict.get("overall_bookmark") or 0),
            "distance": distance_int,
            "address": address,
            "image": img,
        }

    async def get_or_create_place(self, place_name: str, longitude: Optional[float] = None, latitude: Optional[float] = None) -> PlaceResponse:
        norm_name = self._normalize_name(place_name)
        if not norm_name:
            raise HTTPException(status_code=400, detail="유효하지 않은 장소 이름입니다.")

        # 1) DB 우선 조회 (이름)
        row = self.repo.get_place_by_name(norm_name)
        place_dict = self._row_to_place_dict(row)
        if place_dict:
            # 거리 계산 위해 Kakao에서 좌표만 보조 조회
            distance_override = None
            if longitude is not None and latitude is not None:
                kakao = await self._fetch_from_kakao(norm_name) or {}
                dx, dy = kakao.get("longitude"), kakao.get("latitude")
                if isinstance(dx, (int, float)) and isinstance(dy, (int, float)):
                    distance_override = self._compute_distance_m(longitude, latitude, dx, dy)
            payload = self._to_response_payload(place_dict, norm_name, distance_override=distance_override)
            if not payload.get("image"):
                payload["image"] = await self._fetch_image_from_tourapi(payload["place_name"]) or ""
            return PlaceResponse(**payload)

        # 2) Kakao Local 조회
        source = await self._fetch_from_kakao(norm_name)
        if not source:
            raise HTTPException(status_code=404, detail="외부 데이터 없음")

        # 2-1) 주소 중복 체크: 동일 주소의 place가 있으면 그 레코드를 반환
        addr = (source.get("address") or "").strip()
        if addr:
            by_addr = self.repo.get_place_by_address(addr)
            if by_addr:
                by_addr_dict = self._row_to_place_dict(by_addr) or {}
                # 거리 계산 (Kakao 좌표 사용)
                distance_override = None
                if longitude is not None and latitude is not None:
                    dx, dy = source.get("longitude"), source.get("latitude")
                    if isinstance(dx, (int, float)) and isinstance(dy, (int, float)):
                        distance_override = self._compute_distance_m(longitude, latitude, dx, dy)
                payload = self._to_response_payload(by_addr_dict, norm_name, distance_override=distance_override)
                if not payload.get("image"):
                    payload["image"] = await self._fetch_image_from_tourapi(payload["place_name"]) or ""
                return PlaceResponse(**payload)

        # 3) DB에 최소 정보 생성 (주소 중복 없을 때만)
        new_place_id = uuid4()
        try:
            self.repo.create_place(
                place_id=new_place_id,
                name=source.get("name") or norm_name,
                address=source.get("address"),
            )
        except Exception:
            pass

        # 4) 거리 계산
        distance_override = None
        if longitude is not None and latitude is not None:
            dx, dy = source.get("longitude"), source.get("latitude")
            if isinstance(dx, (int, float)) and isinstance(dy, (int, float)):
                distance_override = self._compute_distance_m(longitude, latitude, dx, dy)

        payload = self._to_response_payload(source, norm_name, place_id=str(new_place_id), distance_override=distance_override)
        if not payload.get("image"):
            payload["image"] = await self._fetch_image_from_tourapi(payload["place_name"]) or ""
        return PlaceResponse(**payload)
