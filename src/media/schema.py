from uuid import UUID

from pydantic import BaseModel

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class MediaFindIn(BaseModel):
    object_name: str
    version_id: str


class UserId(BaseModel):
    user_id: UUID
