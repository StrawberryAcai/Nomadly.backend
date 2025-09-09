import uuid
from pydantic import BaseModel


class InterestResponse(BaseModel):
    id: int
    user_id: uuid.UUID
    interest: str