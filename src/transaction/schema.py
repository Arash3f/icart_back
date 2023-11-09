import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schema import Duration
from src.transaction.models import (
    TransactionValueType,
    TransactionReasonEnum,
    TransactionStatusEnum,
)


class TransactionChartType(enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


# ---------------------------------------------------------------------------
class TransactionBase(BaseModel):
    value: float
    text: str
    value_type: TransactionValueType
    status: TransactionStatusEnum
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class TransactionCreate(TransactionBase):
    # ! Relation
    receiver_id: UUID
    transferor_id: UUID
    reason: TransactionReasonEnum
    code: str | None = None


# ---------------------------------------------------------------------------
class TransactionRead(TransactionBase):
    id: UUID
    code: str | None = None
    reason: TransactionReasonEnum | None

    created_at: datetime
    updated_at: datetime | None

    # ! Relation
    receiver_id: UUID
    transferor_id: UUID


# ---------------------------------------------------------------------------
class TransactionFilter(BaseModel):
    gt_value: float | None = None
    lt_value: float | None = None
    value_type: TransactionValueType | None = None
    gt_created_date: datetime | None = None
    lt_created_date: datetime | None = None
    reason: TransactionReasonEnum | None = None


# ---------------------------------------------------------------------------
class TransactionChartFilter(BaseModel):
    type: TransactionChartType
    duration: Duration
    unit: int


# ---------------------------------------------------------------------------
class TransactionAggregateResponse(BaseModel):
    cache: int
    credit: int
