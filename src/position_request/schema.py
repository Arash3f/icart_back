import uuid

from pydantic import BaseModel, ConfigDict

from src.auth.schema import UserBase
from src.contract.schema import ContractRead
from src.location.schema import LocationBase
from src.position_request.models import (
    PositionRequestStatusType,
    PositionRequestType,
)


# ---------------------------------------------------------------------------
class PositionRequestBase(BaseModel):
    is_approve: bool
    field_of_work: str | None
    postal_code: str | None
    tel: str | None
    address: str | None
    employee_count: int | None
    target_position: PositionRequestType
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class PositionRequestCreate(BaseModel):
    requester_username: str | None = None
    target_position: PositionRequestType
    location_id: uuid.UUID
    code: int


# ---------------------------------------------------------------------------
class PositionRequestRead(PositionRequestBase):
    id: uuid.UUID
    status: PositionRequestStatusType

    # ! Relations
    requester_user: UserBase
    next_approve_user: UserBase | None
    contract: ContractRead
    location: LocationBase
    creator: UserBase


# ---------------------------------------------------------------------------
class PositionRequestApproveIn(BaseModel):
    position_request_id: uuid.UUID
    is_approve: bool
