from pydantic import BaseModel
from uuid import UUID

class RatingResponse(BaseModel):
    place_id: UUID
    average_rating: float
    total_ratings: int