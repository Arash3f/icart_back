from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.role.schema import RoleRead


# ---------------------------------------------------------------------------
class UserBase(BaseModel):
    username: str


# ---------------------------------------------------------------------------
class UserRead(UserBase):
    id: UUID
    is_active: bool
    first_name: str | None
    last_name: str | None
    subscribe_newsletter: bool | None


# ---------------------------------------------------------------------------
class CreateUser(BaseModel):
    username: str
    password: str


# ---------------------------------------------------------------------------
class UserReadWithRole(UserRead):
    role: RoleRead

    created_at: datetime
    updated_at: datetime | None
