from fastapi import APIRouter, HTTPException, Path
from locations.model.response.place import PlaceResponse
from locations.service.place import PlaceService

router = APIRouter(prefix="/api/locations/place", tags=["장소"])

@router.get(
    "/{place_name}",
    response_model=PlaceResponse,
    summary="장소 조회 또는 생성",
    description=(
        "주어진 장소 이름으로 장소를 조회합니다.\n"
        "- 존재하면 기존 장소 정보를 반환합니다.\n"
        "- 존재하지 않으면 새 장소를 생성한 뒤 반환합니다.\n"
        "이름 양끝의 따옴표는 제거되고, 제어문자는 필터링됩니다."
    ),
    response_description="요청한 장소 정보",
    responses={
        200: {
            "description": "장소 정보를 반환합니다.",
            "content": {
                "application/json": {
                    "example": {
                        "place_id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "스타벅스 강남점",
                        "address": "서울특별시 강남구 테헤란로 00",
                        "overall_rating": 4.5,
                        "overall_bookmark": 10,
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
    )
):
    service = PlaceService()
    return service.get_or_create_place(place_name)