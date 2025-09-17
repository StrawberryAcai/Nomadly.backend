import os
from decimal import Decimal
from typing import Any, Dict, List
from haversine import haversine
from tourapi.client import TourAPIClient
from uuid import uuid4

from locations.repository.place import PlaceRepository
from locations.constants import CONTENTTYPE
from locations.model.response.response import RecommendResponse

def _to_float(v, default=0.0) -> float:
    if v is None:
        return default
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return default
    return default

def _to_int(v, default=0) -> int:
    if v is None:
        return default
    if isinstance(v, Decimal):
        return int(v)
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    if isinstance(v, str):
        try:
            return int(v)
        except ValueError:
            try:
                return int(float(v))
            except ValueError:
                return default
    return default

def _distance_int(meters: float) -> int:
    return int(round(_to_float(meters, 0.0)))

async def recommend(typeId: int, longitude: float, latitude: float) -> RecommendResponse:
    max_distance_m = 10_000

    api_key = os.getenv("TOURAPI_KEY")
    print(api_key)
    if not api_key:
        raise ValueError("TOURAPI_KEY 환경 변수가 설정되지 않았습니다.")
    client = TourAPIClient(api_key)

    place_repo = PlaceRepository()
    type_name = next((k for k, v in CONTENTTYPE.items() if v == typeId), str(typeId))

    api_resp: Dict[str, Any] = await client.get_location_based_list(
        arrange="Q",
        content_type_id=typeId,
        map_x=longitude,
        map_y=latitude,
        radius=max_distance_m,
    )

    items = (
        api_resp.get("response", {})
                .get("body", {})
                .get("items", {})
                .get("item", [])
    )
    if not isinstance(items, list):
        items = [items] if items else []

    origin = (latitude, longitude)
    results: List[Dict[str, Any]] = []

    for item in items:
        if not item:
            continue

        title = str(item.get("title", "")).strip()
        img = item.get("firstimage")
        if not img:
            continue

        dest_y = _to_float(item.get("mapy"))
        dest_x = _to_float(item.get("mapx"))
        if dest_x == 0.0 or dest_y == 0.0:
            continue

        try:
            distance_m = haversine(origin, (dest_y, dest_x), unit="m")
        except Exception:
            continue

        # TourAPI 주소 추출 (addr1 우선, 없으면 addr2)
        tour_addr = str(item.get("addr1") or item.get("addr2") or "").strip()

        # 주소로 우선 매칭 → 이름으로 보조 매칭 → 없으면 생성
        place_info = None
        if tour_addr:
            place_info = place_repo.get_place_by_address(tour_addr)
        if not place_info and title:
            place_info = place_repo.get_place_by_name(title)
        if not place_info:
            try:
                place_info = place_repo.create_place(
                    place_id=uuid4(),
                    name=title or "미상",
                    address=tour_addr or None,
                )
            except Exception:
                place_info = None

        # DB 레코드 기반으로 응답 필드 정리
        rating = 0.0
        bookmark_cnt = 0
        address = tour_addr
        place_id_val = None
        if place_info:
            if isinstance(place_info, dict):
                rating = _to_float(place_info.get("overall_rating"), 0.0)
                bookmark_cnt = _to_int(place_info.get("overall_bookmark"), 0)
                address = place_info.get("address") or tour_addr or ""
                place_id_val = place_info.get("place_id")
            else:
                # SELECT place_id, name, address, overall_rating, overall_bookmark
                try:
                    rating = _to_float(place_info[3], 0.0)
                    bookmark_cnt = _to_int(place_info[4], 0)
                    address = place_info[2] or tour_addr or ""
                    place_id_val = place_info[0]
                except Exception:
                    rating = 0.0
                    bookmark_cnt = 0
                    address = tour_addr or ""
                    place_id_val = None

        trend = bookmark_cnt > 100

        results.append({
            "place_id": place_id_val or str(uuid4()),
            "place_name": title,
            "rating": float(rating),
            "trend": bool(trend),
            "bookmark_cnt": int(bookmark_cnt),
            "distance": _distance_int(distance_m),
            "address": address,
            "image": str(img),
        })

    return RecommendResponse(
        type=type_name,
        items=results
    )