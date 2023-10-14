import uuid
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.user.schema import UserCreditCashRead


# ---------------------------------------------------------------------------
class WalletBase(BaseModel):
    number: int
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class WalletUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cash_balance: int | None = None
    credit_balance: int | None = None


# ---------------------------------------------------------------------------
class WalletRead(WalletBase):
    id: uuid.UUID
    cash_balance: int
    credit_balance: int

    created_at: datetime
    updated_at: datetime | None

    # ! relations
    user: UserCreditCashRead


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
