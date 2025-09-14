from pydantic import BaseModel
from typing import Optional

class PlaceRequest(BaseModel):
    name: str
    address: Optional[str] = None