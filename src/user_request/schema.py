from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.location.schema import LocationRead
from src.schema import IDRequest
from src.user.schema import UserRead


# ---------------------------------------------------------------------------
class UserRequestBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    birth_place: str | None = None
    postal_code: str | None = None
    father_name: str | None = None
    tel: str | None = None
    address: str | None = None
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class UserRequestRead(UserRequestBase):
    id: UUID
    reason: str | None = None

    created_at: datetime
    updated_at: datetime | None

    # ! Relations
    user: UserRead
    location: LocationRead | None = None


# ---------------------------------------------------------------------------
class CreateUserRequestData(UserRequestBase):
    location_id: UUID | None = None


# ---------------------------------------------------------------------------
class CreateUserRequest(UserRequestBase):
    location_id: UUID | None = None
    user_id: UUID


# ---------------------------------------------------------------------------
class UpdateUserRequest(UserRequestBase):
    location_id: UUID | None = None
    reason: str | None = None
    user_id: UUID


# ---------------------------------------------------------------------------
class ApproveUserRequest(BaseModel):
    where: IDRequest
    data: UpdateUserRequest


# ---------------------------------------------------------------------------
class UserRequestFilter(BaseModel):
    first_name: None | str = None
    location_id: None | UUID = None
    last_name: None | str = None
    gt_created_date: datetime | None = None
    lt_created_date: datetime | None = None
