from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class PosBase(BaseModel):
    number: str

    # ! Relations
    merchant_id: UUID

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class PosCreate(PosBase):
    pass


# ---------------------------------------------------------------------------
class PosUpdate(BaseModel):
    where: IDRequest
    data: PosBase


# ---------------------------------------------------------------------------
class PosRead(PosBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class PosFilter(BaseModel):
    merchant_id: UUID | None = None


# ---------------------------------------------------------------------------
class ConfigPosInput(BaseModel):
    pos_number: str
    merchant_number: str


# ---------------------------------------------------------------------------
class BalanceInput(ConfigPosInput):
    card_number: str
    password: str


# ---------------------------------------------------------------------------
class BalanceOutput(ConfigPosInput):
    amount: int


# ---------------------------------------------------------------------------
class PurchaseInput(ConfigPosInput):
    card_number: str
    password: str
    amount: int


# ---------------------------------------------------------------------------
class PurchaseOutput(BaseModel):
    amount: int
    code: str
    merchant_name: str
