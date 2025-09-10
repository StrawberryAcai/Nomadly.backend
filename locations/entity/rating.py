import uuid

from pydantic import BaseModel


class Rating(BaseModel):
    rating_id: uuid.UUID
    user_id: uuid.UUID
    place_id: uuid.UUID
    score: float