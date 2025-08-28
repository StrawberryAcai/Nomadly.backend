from typing import Dict
from pydantic import BaseModel, Field

class Origin(BaseModel):
    latitude: float
    longitude: float

class DestinationOut(BaseModel):
    distance: float = Field(ge=0)
    address: str

class DistanceResponse(BaseModel):
    origin: Origin
    destinations: Dict[str, DestinationOut]
