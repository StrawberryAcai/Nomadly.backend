from pydantic import BaseModel, Field, confloat
from typing import List
from locations.model.response.place import *

class RecommendResponse(BaseModel):
    type: PlaceType = Field(..., description="요청 때 사용되었던 타입")
    items: List[Place] = Field(..., description="장소와 그 세부 사항의 리스트")