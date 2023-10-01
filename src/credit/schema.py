import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class CreditBase(BaseModel):
    received: float
    consumed: float
    remaining: float
    transferred: float
    debt: float
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CreditRead(CreditBase):
    id: uuid.UUID

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class CreditFilterOrderFild(Enum):
    received = "received"
    consumed = "consumed"
    remaining = "remaining"
    transferred = "transferred"
    debt = "debt"


# ---------------------------------------------------------------------------
class CreditFilterOrderBy(BaseModel):
    desc: list[CreditFilterOrderFild] = []
    asc: list[CreditFilterOrderFild] = []


# ---------------------------------------------------------------------------
class CreditFilter(BaseModel):
    order_by: CreditFilterOrderBy | None = None
