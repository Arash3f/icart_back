import uuid
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class WalletBase(BaseModel):
    number: str
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class WalletRead(WalletBase):
    id: uuid.UUID
    cash_balance: int
    credit_balance: int

    created_at: datetime
    updated_at: datetime | None

    # ! relations
    user_id: uuid.UUID


# ---------------------------------------------------------------------------
class WalletInitCreate(WalletBase):
    number: str
    user_id: UUID | None
