from fastapi import APIRouter, HTTPException, Path, Query, Header
from locations.model.response.place import PlaceResponse, PlaceDetailResponse
from locations.service.place import PlaceService

router = APIRouter(prefix="/api/locations/place", tags=["장소"])

@router.get(
    "/detail",
    response_model=PlaceDetailResponse,
    summary="장소 상세 조회",
    description="""
# Description

ID(UUID) 또는 장소의 주소/이름으로 상세 정보를 조회합니다. DB에 의존하지 않고 외부 데이터만 사용합니다.

# Note

- Kakao Local REST API로 좌표를 조회합니다.
- 실패 시 TourAPI [키워드 검색(searchKeyword2)] 결과로 보조합니다.
- 인증 불필요.

# Request

Query

- q: string (UUID 또는 주소/이름)
- longitude: number? 현재 위치 경도 (미사용)
- latitude: number? 현재 위치 위도 (미사용)

예시

```
GET /api/locations/place/detail?q=스타벅스%20강남점
GET /api/locations/place/detail?q=123e4567-e89b-12d3-a456-426614174000
```

# Response

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| place_name | str | O | 장소 이름 |
| longitude | number | O | 경도 |
| latitude | number | O | 위도 |
| description | str | O | 한줄 설명(주소/개요 등) |

예시

```json
{
  "place_name": "스타벅스 강남점",
  "longitude": 127.0276,
  "latitude": 37.4979,
  "description": "서울특별시 강남구 테헤란로 ..."
}
```

오류

- 400: 유효하지 않은 입력
- 404: 장소 없음
- 500: 내부 처리 오류
""",
)
async def get_place_detail(
    q: str = Query(..., description="장소 ID(UUID) 또는 주소/이름"),
    longitude: float | None = Query(default=None, description="현재 위치 경도"),
    latitude: float | None = Query(default=None, description="현재 위치 위도"),
    Authorization: str | None = Header(default=None),
):
    service = PlaceService()
    return await service.get_place_detail(q, longitude=longitude, latitude=latitude, authorization=Authorization)

@router.get(
    "/{place_name}",
    response_model=PlaceResponse,
    summary="장소 조회 또는 생성",
    description="""
# Description

이름으로 장소를 조회합니다. 존재하지 않으면 외부 데이터(Kakao Local)를 이용해 최소 정보로 생성 후 반환합니다.

이미지가 없으면 TourAPI 검색으로 대표 이미지를 보조 조회합니다.

# Note

- Kakao Local REST API를 사용해 장소 기본정보/좌표를 조회합니다.
- 이미지가 비어있으면 TourAPI [키워드 검색(searchKeyword2)]로 firstimage를 시도합니다.
- 인증 불필요.

# Request

Path

- place_name: string (따옴표 제거/제어문자 필터링 처리됨)

Query

- longitude: number? 현재 위치 경도
- latitude: number? 현재 위치 위도

예시

```
GET /api/locations/place/스타벅스%20강남점?longitude=127.0276&latitude=37.4979
```

# Response

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| place_id | UUID | O | 장소 식별자 |
| place_name | str | O | 장소 이름 |
| rating | number | O | 평점(0~5) |
| trend | bool | O | 방문객 증가 여부 |
| bookmark_cnt | int | O | 북마크 수 |
| distance | int | O | 현재 위치 기준 거리(m) |
| address | str | O | 주소 |
| image | str | O | 대표 이미지 URL |

예시

```json
{
  "place_id": "123e4567-e89b-12d3-a456-426614174000",
  "place_name": "스타벅스 강남점",
  "rating": 4.5,
  "trend": false,
  "bookmark_cnt": 10,
  "distance": 240,
  "address": "서울특별시 강남구 테헤란로 ...",
  "image": "https://example.com/image.jpg"
}
```

오류

- 400: 유효하지 않은 장소 이름
- 404: 외부 데이터 없음
- 500: 내부 처리 오류
""",
    response_description="요청한 장소 정보",
    responses={
        200: {
            "description": "장소 정보를 반환합니다.",
            "content": {
                "application/json": {
                    "example": {
                        "place_id": "123e4567-e89b-12d3-a456-426614174000",
                        "place_name": "스타벅스 강남점",
                        "address": "서울특별시 강남구 테헤란로 00",
                        "rating": 4.5,
                        "bookmark_cnt": 10,
                        "trend": False,
                        "distance": 0,
                        "image": "https://example.com/image.jpg"
                    }
                }
            },
        },
        400: {
            "description": "잘못된 요청(장소 이름이 유효하지 않음).",
            "content": {
                "application/json": {
                    "example": {"detail": "유효하지 않은 장소 이름입니다."}
                }
            },
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "examples": {
                        "parse_error": {
                            "summary": "결과 파싱 오류",
                            "value": {"detail": "장소 생성 결과를 해석할 수 없습니다."},
                        },
                        "create_error": {
                            "summary": "생성 처리 중 오류",
                            "value": {"detail": "장소 생성 중 오류: ..."},
                        },
                    }
                }
            },
        },
    },
)
async def get_or_create_place(
    place_name: str = Path(
        ...,
        description="조회하거나 생성할 장소 이름",
        example="스타벅스 강남점",
    ),
    longitude: float | None = Query(default=None, description="현재 위치 경도"),
    latitude: float | None = Query(default=None, description="현재 위치 위도"),
    Authorization: str | None = Header(default=None),
):
    service = PlaceService()
    return await service.get_or_create_place(place_name, longitude=longitude, latitude=latitude, authorization=Authorization)