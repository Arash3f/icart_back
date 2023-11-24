from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.location.schema import LocationRead
from src.schema import IDRequest
from src.user.schema import UserRead


# ---------------------------------------------------------------------------
class UserRequestBase(BaseModel):
    birth_place: str | None = None
    postal_code: str | None = None
    father_name: str | None = None
    tel: str | None = None
    address: str | None = None

    national_card_front_version_id: str | None
    national_card_back_version_id: str | None
    birth_certificate_version_id: str | None
    video_version_id: str | None

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class UserRequestRead(UserRequestBase):
    id: UUID
    reason: str | None = None
    status: bool | None = None

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
    status: bool | None = None
