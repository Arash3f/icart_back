import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.capital_transfer.models import CapitalTransferEnum, CapitalTransferStatusEnum
from src.schema import IDRequest
from src.transaction.models import TransactionStatusEnum


# ---------------------------------------------------------------------------
class CapitalTransferBase(BaseModel):
    transfer_type: CapitalTransferEnum
    value: int
    status: TransactionStatusEnum
    model_config = ConfigDict(extra="forbid")

    file_version_id: str | None = None
    file_name: str | None = None

    # ! Relations
    receiver_id: uuid.UUID | None = None
    transaction_id: uuid.UUID | None = None


# ---------------------------------------------------------------------------
class CapitalTransferCreate(CapitalTransferBase):
    code: int


# ---------------------------------------------------------------------------
class CapitalTransferUpdate(BaseModel):
    finish: bool
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CapitalTransferRead(CapitalTransferBase):
    id: uuid.UUID
    code: int
    finish: bool
    status: CapitalTransferStatusEnum

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class CapitalTransferFilterOrderFild(Enum):
    value = "value"
    transfer_type = "transfer_type"
    finish = "finish"


# ---------------------------------------------------------------------------
class CapitalTransferFilterOrderBy(BaseModel):
    desc: list[CapitalTransferFilterOrderFild] = []
    asc: list[CapitalTransferFilterOrderFild] = []


# ---------------------------------------------------------------------------
class CapitalTransferFilter(BaseModel):
    gt_value: float | None = None
    lt_value: float | None = None
    transfer_type: None | CapitalTransferEnum = None
    receiver_id: None | UUID = None
    finish: None | bool = None
    code: None | str = None
    status: CapitalTransferStatusEnum | None = None
    order_by: CapitalTransferFilterOrderBy | None = None


# ---------------------------------------------------------------------------
class CapitalTransferApprove(BaseModel):
    where: IDRequest
    approve: bool
