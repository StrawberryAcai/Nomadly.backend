# plan/model/response/ai_plan.py
from __future__ import annotations
from pydantic import BaseModel, Field, StringConstraints
from typing import List, Annotated

DateStr = Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2}$")]
DateTimeStr = Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}$")]  # yyyy-mm-dd-hh-MM

class PlanItem(BaseModel):
    todo: str
    place: str
    time: DateTimeStr

class AIPlanResponse(BaseModel):
    start_date: DateStr
    end_date: DateStr
    plan: List[List[PlanItem]] = Field(..., description="plan[n]은 n+1일")
