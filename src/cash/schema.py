import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class CashBase(BaseModel):
    received: int
    consumed: int
    transferred: int
    debt: int
    balance: int
    cash_back: int
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CashBalanceResponse(BaseModel):
    balance: int
    cash_back: int
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CashRead(CashBase):
    id: uuid.UUID


# ---------------------------------------------------------------------------
class CashFilterOrderFild(Enum):
    received = "received"
    consumed = "consumed"
    remaining = "remaining"
    transferred = "transferred"
    debt = "debt"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class CashFilterOrderBy(BaseModel):
    desc: list[CashFilterOrderFild] = []
    asc: list[CashFilterOrderFild] = []


# ---------------------------------------------------------------------------
class CashFilter(BaseModel):
    national_code: None | str = None
    phone_number: None | str = None
    name: str | None = None
    order_by: CashFilterOrderBy | None = None
