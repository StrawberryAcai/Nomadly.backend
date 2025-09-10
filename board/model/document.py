import uuid

from pydantic import BaseModel


class BoardResponse(BaseModel):
    board_id: uuid.UUID
    title: str
    content: str
    is_liked: bool
    likes: int

class BoardDetailResponse(BaseModel):
    board_id: uuid.UUID
    title: str
    content: str
    is_liked: bool
    likes: int
    plan: dict