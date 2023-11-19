import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.user.schema import UserCreditCashRead, UserReadV2


# ---------------------------------------------------------------------------
class WalletBase(BaseModel):
    number: int
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class WalletRead(WalletBase):
    id: uuid.UUID

    created_at: datetime
    updated_at: datetime | None

    # ! relations
    user: UserCreditCashRead


class WalletReadV2(BaseModel):
    user: UserReadV2 | None = None


# ---------------------------------------------------------------------------
class WalletBalanceRead(BaseModel):
    cash_balance: int
    credit_balance: int


# ---------------------------------------------------------------------------
class WalletInitCreate(WalletBase):
    number: str
    user_id: UUID | None


# ---------------------------------------------------------------------------
class WalletAdditionalInfo(BaseModel):
    income: int | None = 0
    credit_consumed: int | None = 0
    debt_to_acceptor: int | None = 0
    settled_amount: int | None = 0
    credit_amount: int | None = 0
    organizations_count: int | None = 0
    merchant_count: int | None = 0
    transaction_count: int | None = 0
    organization_users: int | None = 0
    unsettled_credit: int | None = 0
    received_credit: int | None = 0
    paid_credit: int | None = 0
    used_credit: int | None = 0


# ---------------------------------------------------------------------------
class WalletFilterOrderFild(Enum):
    number = "number"
    is_lock = "is_lock"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class WalletFilterOrderBy(BaseModel):
    desc: list[WalletFilterOrderFild] = []
    asc: list[WalletFilterOrderFild] = []


# ---------------------------------------------------------------------------
class WalletFilter(BaseModel):
    name: str | bool | None = None
    national_code: str | bool | None = None
    number: str | bool | None = None
    is_lock: bool | None = None
    order_by: WalletFilterOrderBy | None = None
