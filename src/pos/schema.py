import enum
from datetime import datetime
from uuid import UUID

from jdatetime import datetime as jdatetime
from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


class PosPurchaseType(enum.Enum):
    DIRECT = "DIRECT"
    CREDIT = "CREDIT"


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
    terminal_number: str
    merchant_number: str


# ---------------------------------------------------------------------------
class ConfigurationPosInput(BaseModel):
    username: str
    password: str


# ---------------------------------------------------------------------------
class ConfigurationPosOutput(BaseModel):
    terminal_number: str
    password: str
    tel: str | None = None
    date_time: str


# ---------------------------------------------------------------------------
class ConfigPosOutput(BaseModel):
    merchant_name: str


# ---------------------------------------------------------------------------
class BalanceInput(ConfigPosInput):
    card_track: str
    password: str


# ---------------------------------------------------------------------------
class BalanceOutput(ConfigPosInput):
    amount: int
    code: int
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
