from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.auth.schema import UserBase
from src.location.schema import LocationRead
from src.schema import IDRequest


# ---------------------------------------------------------------------------
class UserRequestBase(BaseModel):
    birth_place: str | None = None
    postal_code: str | None = None
    tel: str | None = None
    address: str | None = None

    national_card_front_version_id: str | None = None
    national_card_back_version_id: str | None = None
    birth_certificate_version_id: str | None = None
    video_version_id: str | None = None

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class UserRequestRead(UserRequestBase):
    id: UUID | None = None
    reason: str | None = None
    detail: str | None = None
    status: bool | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    # ! Relations
    user: UserBase | None = None
    location: LocationRead | None = None


# ---------------------------------------------------------------------------
class CreateUserRequestData(BaseModel):
    birth_place: str | None = None
    postal_code: str | None = None
    tel: str | None = None
    address: str | None = None
    location_id: UUID | None = None


# ---------------------------------------------------------------------------
class CreateUserRequest(UserRequestBase):
    location_id: UUID | None = None
    user_id: UUID


# ---------------------------------------------------------------------------
class UpdateUserRequest(BaseModel):
    is_approve: bool
    reason: str | None = None
    detail: str | None = None


# ---------------------------------------------------------------------------
class ApproveUserRequest(BaseModel):
    where: IDRequest
    data: UpdateUserRequest


# ---------------------------------------------------------------------------
class UserRequestFilter(BaseModel):
    status: bool | None = None
    location_id: UUID | None = None
    national_code: str | None = None
