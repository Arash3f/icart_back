from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.invoice.models import InvoiceTypeEnum
from src.schema import IDRequest


# ---------------------------------------------------------------------------
class InvoiceBase(BaseModel):
    number: str
    value: int
    type: InvoiceTypeEnum
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class InvoiceCreate(InvoiceBase):
    # ! Relation
    parent_number: str | None = None
    merchant_number: str


# ---------------------------------------------------------------------------
class InvoiceVerifyInput(BaseModel):
    number: str

    # ! Relations
    merchant_number: str


# ---------------------------------------------------------------------------
class InvoiceVerifyOutput(InvoiceBase):
    # ! Relations
    parent_number: str | None = None
    transferor_wallet_number: str | None = None
    tracing_number: str | None = None


# ---------------------------------------------------------------------------
class InvoiceUpdateInput(BaseModel):
    where: IDRequest
    data: InvoiceCreate
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class InvoiceNumberInput(BaseModel):
    number: str


# ---------------------------------------------------------------------------
class InvoiceRead(InvoiceBase):
    icart_number: int

    created_at: datetime
    updated_at: datetime | None
