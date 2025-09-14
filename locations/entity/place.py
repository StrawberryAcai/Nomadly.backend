import uuid

from pydantic import BaseModel


class Place(BaseModel):
    place_id: uuid.UUID
    name: str
    address: str
    overall_rating: float
    overall_bookmark: int