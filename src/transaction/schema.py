import enum
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.card.schema import CardReadV2
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
class TransactionRowBase(BaseModel):
    value: float
    text: str
    value_type: TransactionValueType
    status: TransactionStatusEnum
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class TransactionRowCreate(TransactionRowBase):
    # ! Relation
    transaction_id: UUID
    receiver_id: UUID
    transferor_id: UUID
    zibal_track_id: str | None = None
    reason: TransactionReasonEnum
    code: int | None = None


# ---------------------------------------------------------------------------
class TransactionRowRead(TransactionRowBase):
    id: UUID
    code: int | None = None
    reason: TransactionReasonEnum | None

    created_at: datetime
    updated_at: datetime | None

    # # ! Relation
    receiver: CardReadV2
    transferor: CardReadV2


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
    code: int | None = None


# ---------------------------------------------------------------------------
class TransactionRead(TransactionBase):
    id: UUID
    code: int | None = None
    reason: TransactionReasonEnum | None

    created_at: datetime
    updated_at: datetime | None

    # ! Relation
    transactions_rows: list[TransactionRowRead] | None = []
    receiver: CardReadV2
    transferor: CardReadV2


# ---------------------------------------------------------------------------
class TransactionFilterOrderFild(Enum):
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class TransactionFilterOrderBy(BaseModel):
    desc: list[TransactionFilterOrderFild] = []
    asc: list[TransactionFilterOrderFild] = []


# ---------------------------------------------------------------------------
class TransactionFilter(BaseModel):
    gt_value: float | None = None
    lt_value: float | None = None
    value_type: TransactionValueType | None = None
    gt_created_date: datetime | None = None
    lt_created_date: datetime | None = None
    card_number: None | str = None
    order_by: TransactionFilterOrderBy | None = None


# ---------------------------------------------------------------------------
class TransactionChartFilter(BaseModel):
    type: TransactionChartType
    duration: Duration
    unit: int


# ---------------------------------------------------------------------------
class TransactionAggregateResponse(BaseModel):
    cache: int
    credit: int
