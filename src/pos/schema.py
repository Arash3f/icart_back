import enum
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


class PosPurchaseType(enum.Enum):
    DIRECT = "DIRECT"
    CREDIT = "CREDIT"


class CardBalanceType(enum.Enum):
    CASH = "CASH"
    CREDIT = "CREDIT"


# ---------------------------------------------------------------------------
class PosBase(BaseModel):
    number: str

    # ! Relations
    merchant_id: UUID

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class PosCreate(BaseModel):
    # ! Relations
    merchant_id: UUID


# ---------------------------------------------------------------------------
class PosUpdateData(BaseModel):
    number: str


# ---------------------------------------------------------------------------
class PosUpdate(BaseModel):
    where: IDRequest
    data: PosUpdateData


# ---------------------------------------------------------------------------
class PosRead(PosBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class PosFilterOrderFild(Enum):
    number = "number"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class PosFilterOrderBy(BaseModel):
    desc: list[PosFilterOrderFild] = []
    asc: list[PosFilterOrderFild] = []


# ---------------------------------------------------------------------------
class PosFilter(BaseModel):
    merchant_id: UUID | None = None
    name: None | str = None
    national_code: None | str = None
    number: None | str = None
    merchant_number: None | str = None
    order_by: PosFilterOrderBy | None = None


# ---------------------------------------------------------------------------
class ConfigPosInput(BaseModel):
    terminal_number: str
    merchant_number: str


# ---------------------------------------------------------------------------
class ConfigurationPosInput(BaseModel):
    username: str
    password: str


# ---------------------------------------------------------------------------
class ConfigurationPosOutput(BaseModel):
    merchant_name: str
    tel: str | None = None


# ---------------------------------------------------------------------------
class ConfigPosOutput(BaseModel):
    merchant_name: str


# ---------------------------------------------------------------------------
class BalanceInput(ConfigPosInput):
    card_track: str
    password: str


# ---------------------------------------------------------------------------
class BalanceOutput(BaseModel):
    cash_balance: int
    credit_balance: int
    traction_code: int
    date_time: str


# ---------------------------------------------------------------------------
class PurchaseInput(ConfigPosInput):
    card_track: str
    password: str
    amount: int
    type: PosPurchaseType


# ---------------------------------------------------------------------------
class PurchaseOutput(BaseModel):
    amount: int
    fee: int
    traction_code: str
    date_time: str


# ---------------------------------------------------------------------------
class InstallmentsPurchaseInput(ConfigPosInput):
    card_track: str
    password: str
    amount: int
    number_of_installments: int


# ---------------------------------------------------------------------------
class InstallmentsPurchaseOutput(BaseModel):
    amount: int
    traction_code: str
    date_time: str
