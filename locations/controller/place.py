from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID, uuid4
from locations.repository.place import PlaceRepository

router = APIRouter(prefix="/api/locations/place")

# 요청 모델
class PlaceRequest(BaseModel):
    name: str  # 장소 이름
    address: Optional[str] = None  # 장소 주소 (선택적)

# 응답 모델
class PlaceResponse(BaseModel):
    place_id: UUID
    name: str
    address: Optional[str]
    overall_rating: float
    overall_bookmark: int

@router.get("/{place_name}", response_model=PlaceResponse)
async def get_or_create_place(place_name: str):
    """
    장소 정보를 가져오거나, 없으면 새로 생성합니다.
    """
    place_repo = PlaceRepository()

    # 장소 이름으로 검색
    place = place_repo.get_place_by_name(place_name)
    if place:
        return place

    # 장소가 없으면 새로 생성
    try:
        new_place_id = uuid4()
        new_place = place_repo.create_place(
            place_id=new_place_id,
            name=place_name,
            address=None  # 주소는 기본값으로 None
        )
        return new_place
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"장소 생성 중 오류 발생: {str(e)}")