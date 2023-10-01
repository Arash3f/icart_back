import uuid

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class PermissionBase(BaseModel):
    name: str
    code: int
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class PermissionCreate(PermissionBase):
    pass


# ---------------------------------------------------------------------------
class PermissionRead(PermissionBase):
    id: uuid.UUID
