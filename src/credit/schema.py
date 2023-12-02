import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class CreditBase(BaseModel):
    received: int
    consumed: int
    remaining: int
    transferred: int
    considered: int
    paid: int
    debt: int
    balance: int
    active: bool
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CreditBalanceResponse(BaseModel):
    balance: int
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CreditRead(CreditBase):
    id: uuid.UUID


# ---------------------------------------------------------------------------
class CreditFilterOrderFild(Enum):
    received = "received"
    consumed = "consumed"
    remaining = "remaining"
    transferred = "transferred"
    debt = "debt"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class CreditFilterOrderBy(BaseModel):
    desc: list[CreditFilterOrderFild] = []
    asc: list[CreditFilterOrderFild] = []


# ---------------------------------------------------------------------------
class CreditFilter(BaseModel):
    national_code: None | str = None
    phone_number: None | str = None
    name: str | None = None
    last_name: str | None = None
    order_by: CreditFilterOrderBy | None = None
