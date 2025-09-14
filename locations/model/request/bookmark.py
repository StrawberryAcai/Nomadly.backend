from pydantic import BaseModel
from uuid import UUID

class BookmarkRequest(BaseModel):
    place_id: UUID
    user_id: UUID