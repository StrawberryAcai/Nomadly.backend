from pydantic import BaseModel, Field, validator
from locations.model.request.request import *
from typing import Literal, Union
from pydantic import HttpUrl
from uuid import UUID

class PlaceResponse(BaseModel):
    place_id: UUID
    place_name: str
    rating: float = Field(..., ge=0, le=5, description="평점")
    trend: bool = Field(..., description="방문객 증가 여부")
    bookmark_cnt: int = Field(..., description="북마크 카운트")
    distance: int = Field(..., ge=0, le=40075000, description="현재 거리로부터 목적지까지 거리")
    address: str = Field(..., description="주소")
    image: str = Field(..., description="이미지 url")