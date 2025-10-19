from pydantic import BaseModel, Field
from uuid import UUID

class VisibilityUpdateResponse(BaseModel):
    plan_id: UUID = Field(..., description="plan id")
    visibility: str = Field(..., description="public 또는 private")
    success: bool = Field(..., description="변경 성공 여부")
