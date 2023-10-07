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
class WalletInitCreate(WalletBase):
    number: str
    user_id: UUID | None


# ---------------------------------------------------------------------------
class WalletAdditionalInfo(BaseModel):
    income: int | None = None
    transactions: int | None = None
    organization_users: int | None = None
    unsettled_credit: int | None = None
    received_credit: int | None = None
    paid_credit: int | None = None
