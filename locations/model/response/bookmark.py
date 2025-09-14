from pydantic import BaseModel
from uuid import UUID

class BookmarkResponse(BaseModel):
    place_id: UUID
    user_id: UUID
    is_bookmarked: bool