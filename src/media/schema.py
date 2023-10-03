from pydantic import BaseModel


# ---------------------------------------------------------------------------
class MediaFindIn(BaseModel):
    object_name: str
    version_id: str
