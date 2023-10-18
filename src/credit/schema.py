import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class CreditBase(BaseModel):
    received: int
    consumed: int
    remaining: int
    transferred: int
    debt: int
    balance: int
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


# ---------------------------------------------------------------------------
class CreditFilterOrderBy(BaseModel):
    desc: list[CreditFilterOrderFild] = []
    asc: list[CreditFilterOrderFild] = []


# ---------------------------------------------------------------------------
class CreditFilter(BaseModel):
    order_by: CreditFilterOrderBy | None = None
