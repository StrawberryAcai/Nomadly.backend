import uuid
from typing import List

from pydantic.v1 import BaseModel

class PlanItemDetailResponse(BaseModel):
    todo: str
    place: str
    time: str

class PlanDetailResponse(BaseModel):
    start_time: str
    end_time: str
    plan: List[PlanItemDetailResponse]

class MyPlansResponse(BaseModel):
    plan_id: uuid.UUID
    plan: PlanDetailResponse
