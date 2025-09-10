from pydantic import constr
from typing import Literal
from locations.model.request.origin import *

PlaceType = Literal["관광지","문화시설","축제공연행사","여행코스","레포츠","숙박","쇼핑","음식점"]

class RecommendRequest(BaseModel):
    type: PlaceType = Field(..., description="어떠한 주제에 맞추어 장소를 추천하는데 쓰입니다. 자세한 호출 규약은 Notion 참조")
    origin: Origin = Field(..., description="현재 좌표 객체")