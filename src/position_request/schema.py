import uuid
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.ability.schema import AbilityBase
from src.auth.schema import UserBase
from src.contract.schema import ContractRead
from src.location.schema import LocationBase
from src.position_request.models import (
    PositionRequestStatusType,
    PositionRequestType,
    FieldOfWorkType,
    SellingType,
)
from src.schema import IDRequest


# ---------------------------------------------------------------------------
class UserRead(BaseModel):
    national_code: str
    location: LocationBase


# ---------------------------------------------------------------------------
class PositionRequestBase(BaseModel):
    is_approve: bool
    field_of_work: FieldOfWorkType | None
    postal_code: str | None
    tel: str | None
    address: str | None
    employee_count: int | None
    profit_rate: int = 0
    selling_type: SellingType | None
    received_money: str | None = None
    tracking_code: str | None = None
    reason: str | None = None
    geo: str | None = None
    target_position: PositionRequestType

    # ! Relations
    requester_user: UserRead
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
    # location: LocationComplex
    creator: UserBase


# ---------------------------------------------------------------------------
class PositionRequestApproveIn(BaseModel):
    position_request_id: uuid.UUID
    is_approve: bool
    reason: str | None = None


# ---------------------------------------------------------------------------
class PositionRequestFilterOrderFild(Enum):
    field_of_work = "field_of_work"
    target_position = "target_position"
    is_approve = "is_approve"
    status = "status"


# ---------------------------------------------------------------------------
class PositionRequestFilterOrderBy(BaseModel):
    desc: list[PositionRequestFilterOrderFild] = []
    asc: list[PositionRequestFilterOrderFild] = []


# ---------------------------------------------------------------------------
class PositionRequestFilter(BaseModel):
    field_of_work: FieldOfWorkType | None = None
    target_position: PositionRequestType | None = None
    is_approve: bool | None = None
    status: PositionRequestStatusType | None = None
    name: str | None = None
    national_code: str | None = None
    order_by: PositionRequestFilterOrderBy | None = None


# ---------------------------------------------------------------------------
class PositionRequestUpdateData(BaseModel):
    target_position: PositionRequestType
    location_id: UUID
    number: str
    field_of_work: FieldOfWorkType | None = None
    selling_type: SellingType | None = None
    postal_code: str
    tel: str
    address: str
    employee_count: int | None = None
    profit_rate: int = 0
    received_money: str | None = None
    tracking_code: str | None = None
    geo: str | None = None
    name: str
    signatory_name: str
    signatory_position: str


# ---------------------------------------------------------------------------
class PositionRequestUpdate(BaseModel):
    data: PositionRequestUpdateData
    where: IDRequest
