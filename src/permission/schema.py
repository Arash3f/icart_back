import enum
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


# ---------------------------------------------------------------------------
class PermissionFilterOrderFild(enum.Enum):
    name = "name"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class PermissionFilterOrderBy(BaseModel):
    desc: list[PermissionFilterOrderFild] = []
    asc: list[PermissionFilterOrderFild] = []


# ---------------------------------------------------------------------------
class PermissionFilter(BaseModel):
    name: str | None | bool = None
    order_by: PermissionFilterOrderBy | None = None
