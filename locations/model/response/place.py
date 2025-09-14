from pydantic import BaseModel, Field, validator
from locations.model.request.request import *

class PlaceResponse(BaseModel):
    place_name: str
    rating: float = Field(..., ge=0, le=5, description="평점")
    trend: bool = Field(..., description="방문객 증가 여부")
    bookmark_cnt: int = Field(..., description="북마크 카운트")
    distance: int = Field(..., ge=0, le=40075000, description="현재 거리로부터 목적지까지 거리")
    image: str = Field(..., pattern="^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$", description="이미지 url")