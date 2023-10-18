from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class InstallmentsBase(BaseModel):
    number: str
    value: int
    due_date: datetime
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class InstallmentsCreate(InstallmentsBase):
    # ! Relation
    parent_id: UUID | None = None
    merchant_id: UUID
    user_id: UUID
    invoice_id: UUID | None = None


# ---------------------------------------------------------------------------
class InstallmentsRead(InstallmentsBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None

    # ! Relation
    parent_id: UUID | None = None
    merchant_id: UUID
    user_id: UUID
    invoice_id: UUID | None = None


# ---------------------------------------------------------------------------
class InstallmentsFilterOrderFild(Enum):
    due_date = "due_date"


# ---------------------------------------------------------------------------
class InstallmentsFilterOrderBy(BaseModel):
    desc: list[InstallmentsFilterOrderFild] = []
    asc: list[InstallmentsFilterOrderFild] = []


# ---------------------------------------------------------------------------
class InstallmentsFilter(BaseModel):
    user_id: None | bool = None
    order_by: InstallmentsFilterOrderBy | None = None
