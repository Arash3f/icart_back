from uuid import UUID

from pydantic import BaseModel


# ---------------------------------------------------------------------------
class MediaFindIn(BaseModel):
    object_name: str
    version_id: str


class UserId(BaseModel):
    user_id: UUID
