import uuid

from pydantic import BaseModel


class Bookmark(BaseModel):
    bookmark_id: uuid.UUID
    user_id: uuid.UUID
    place_id: uuid.UUID