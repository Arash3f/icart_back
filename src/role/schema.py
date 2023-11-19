import enum
import uuid
from datetime import datetime

from pydantic import BaseModel

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class RoleBase(BaseModel):
    name: str


# ---------------------------------------------------------------------------
class RoleCreate(RoleBase):
    pass


# ---------------------------------------------------------------------------
class RoleUpdate(BaseModel):
    where: IDRequest
    data: RoleBase


# ---------------------------------------------------------------------------
class RoleRead(RoleBase):
    id: uuid.UUID


# ---------------------------------------------------------------------------
class RolePermissionBase(BaseModel):
    role_id: uuid.UUID
    permission_id: uuid.UUID


# ---------------------------------------------------------------------------
class RolePermissionCreate(RolePermissionBase):
    pass


# ---------------------------------------------------------------------------
class PermissionsToRole(BaseModel):
    role_id: uuid.UUID
    permission_ids: list[uuid.UUID]

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class RoleFilterOrderFild(enum.Enum):
    name = "name"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class RoleFilterOrderBy(BaseModel):
    desc: list[RoleFilterOrderFild] = []
    asc: list[RoleFilterOrderFild] = []


# ---------------------------------------------------------------------------
class RoleFilter(BaseModel):
    name: str | None | bool = None
    order_by: RoleFilterOrderBy | None = None
