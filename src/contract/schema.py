import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from src.location.schema import LocationBase
from src.position_request.models import (
    FieldOfWorkType,
    SellingType,
    PositionRequestStatusType,
    PositionRequestType,
)


# ---------------------------------------------------------------------------
class ContractBase(BaseModel):
    number: str | None = None
    name: str | None = None
    signatory_name: str | None = None
    signatory_position: str | None = None
    employees_number: int | None = None
    file_version_id: str | None = None
    file_name: str | None = None
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class ContractCreate(ContractBase):
    file_version_id: str | None = None
    file_name: str | None = None


# ---------------------------------------------------------------------------
class PositionRequestRead(BaseModel):
    id: uuid.UUID
    field_of_work: FieldOfWorkType | None
    postal_code: str | None
    tel: str | None
    address: str | None
    employee_count: int | None
    selling_type: SellingType | None = None
    model_config = ConfigDict(extra="forbid")

    # ! Relations
    location: LocationBase | None = None


# ---------------------------------------------------------------------------
class ContractRead(ContractBase):
    id: uuid.UUID

    created_at: datetime
    updated_at: datetime | None

    # ! Relation
    position_request: PositionRequestRead


# ---------------------------------------------------------------------------
class ContractFilterOrderFild(Enum):
    number = "number"


# ---------------------------------------------------------------------------
class ContractFilterOrderBy(BaseModel):
    desc: list[ContractFilterOrderFild] = []
    asc: list[ContractFilterOrderFild] = []


# ---------------------------------------------------------------------------
class ContractFilter(BaseModel):
    number: str | None = None
    order_by: ContractFilterOrderBy | None = None
