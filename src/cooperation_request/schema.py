from datetime import datetime
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
    location_id: LocationComplex
