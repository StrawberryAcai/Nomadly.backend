from pydantic import BaseModel, Field
from uuid import UUID

class RatingRequest(BaseModel):
    place_id: UUID
    score: float = Field(..., ge=0.0, le=5.0)
    user_id: UUID