import uuid

from pydantic import BaseModel


class Interest(BaseModel):
    id: int
    user_id: uuid.UUID
    interest: str