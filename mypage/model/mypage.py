import uuid
from typing import List

from pydantic import BaseModel

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

class MyBookmarkResponse(BaseModel):
    place_id: uuid.UUID
    name: str
    address: str
    overall_bookmark: int
    overall_rating: float

class MyLikeBoardResponse(BaseModel):
    board_id: uuid.UUID
    title: str
    content: str
    likes: int