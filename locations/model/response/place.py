from pydantic import BaseModel, Field, confloat, conint, validator
from locations.model.request.request import *

class Place(BaseModel):
    place_name: str
    rating: confloat(ge=0, le=5) = Field(..., description="평점")
    trend: bool = Field(..., description="방문객 증가 여부")
    bookmark_cnt: int = Field(..., description="북마크 카운트")
    # 40,075,000 is circumference of earth
    distance: conint(ge=0, le=40075000) = Field(..., description="현재 거리로부터 목적지까지 거리")
    image: constr(pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$") = Field(..., description="이미지 url")