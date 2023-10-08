import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class CashBase(BaseModel):
    received: int
    consumed: int
    remaining: int
    transferred: int
    debt: int
    balance: int
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CashBalanceResponse(BaseModel):
    balance: int
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CashRead(CashBase):
    id: uuid.UUID

    created_at: datetime


# ---------------------------------------------------------------------------
class CashFilterOrderFild(Enum):
    received = "received"
    consumed = "consumed"
    remaining = "remaining"
    transferred = "transferred"
    debt = "debt"


# ---------------------------------------------------------------------------
class CashFilterOrderBy(BaseModel):
    desc: list[CashFilterOrderFild] = []
    asc: list[CashFilterOrderFild] = []


# ---------------------------------------------------------------------------
class CashFilter(BaseModel):
    order_by: CashFilterOrderBy | None = None
