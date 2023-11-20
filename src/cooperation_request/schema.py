from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.cooperation_request.models import (
    CooperationType,
    CooperationRequestFieldOfWorkType,
)
from src.location.schema import LocationComplex
from src.schema import IDRequest


# ---------------------------------------------------------------------------
class CooperationRequestBase(BaseModel):
    name: str
    tel: str
    requester_name: str
    type: CooperationType

    field_of_work: CooperationRequestFieldOfWorkType | None = None
    employee_count: int | None = None

    model_config = ConfigDict(extra="forbid")

    # ! relations
    location_id: UUID


# ---------------------------------------------------------------------------
class CooperationRequestCreate(CooperationRequestBase):
    pass


# ---------------------------------------------------------------------------
class CooperationRequestUpdateStatusData(BaseModel):
    status: bool


# ---------------------------------------------------------------------------
class CooperationRequestUpdateStatus(BaseModel):
    where: IDRequest
    data: CooperationRequestUpdateStatusData


# ---------------------------------------------------------------------------
class CooperationRequestRead(CooperationRequestBase):
    id: UUID
    status: bool

    created_at: datetime
    updated_at: datetime | None

    # ! relations
    location: LocationComplex


# ---------------------------------------------------------------------------
class CooperationRequestFilterOrderFild(Enum):
    field_of_work = "field_of_work"
    type = "type"
    status = "status"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class CooperationRequestFilterOrderBy(BaseModel):
    desc: list[CooperationRequestFilterOrderFild] = []
    asc: list[CooperationRequestFilterOrderFild] = []


# ---------------------------------------------------------------------------
class CooperationRequestFilter(BaseModel):
    field_of_work: CooperationRequestFieldOfWorkType | None = None
    type: CooperationType | None = None
    requester_name: str | None = None
    status: bool | None = None
    name: str | None = None
    tel: str | None = None
    order_by: CooperationRequestFilterOrderBy | None = None
