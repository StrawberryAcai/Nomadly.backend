# plan/model/request/ai_plan.py
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Annotated, TypeAlias

DateStr: TypeAlias = Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]

class PlanRequest(BaseModel):
    destination: str = Field(..., description="워케이션 혹은 여행 장소 이름")
    start_date: DateStr
    end_date: DateStr
    interests: List[str]
    purpose: str
    activeness: bool
    budget_detail: int
    budget_preset: Literal["low", "medium", "high"]
    companies: Literal["alone", "family", "friends", "couple"] | str
    preferred_time: Literal["morning", "afternoon", "evening"] | str
    bookmarked: List[str] = Field(default_factory=list)

    @field_validator("interests")
    @classmethod
    def _strip_interests(cls, v: List[str]) -> List[str]:
        return [s.strip() for s in v]
