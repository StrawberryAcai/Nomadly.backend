from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal

class VisibilityUpdateRequest(BaseModel):
    plan_id: UUID = Field(..., description="변경할 plan의 id")
    visibility: Literal["public", "private"] = Field(..., description="public 또는 private")
