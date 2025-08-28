from typing import List
from pydantic import BaseModel, Field

class Origin(BaseModel):
    # 위도는 남위 90도, 북위 90도가 범위
    latitude: float = Field(ge=-90, le=90)
    # 경도는 동쪽 180도, 서쪽 180도가 범위
    longitude: float = Field(ge=-180, le=180)

class DestinationIn(BaseModel):
    ref: str
    address: str

class DistanceRequest(BaseModel):
    type: str
    origin: Origin
    destinations: List[DestinationIn]
