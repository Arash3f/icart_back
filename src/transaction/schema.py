from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.transaction.models import TransactionValueType


# ---------------------------------------------------------------------------
class TransactionBase(BaseModel):
    value: float
    text: str
    value_type: TransactionValueType
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class TransactionCreate(TransactionBase):
    # ! Relation
    receiver_id: str
    transferor_id: str


# ---------------------------------------------------------------------------
class TransactionRead(TransactionCreate):
    id: UUID


# ---------------------------------------------------------------------------
class TransactionFilter(BaseModel):
    gt_value: float | None = None
    lt_value: float | None = None
    value_type: TransactionValueType | None = None
    gt_created_date: datetime | None = None
    lt_created_date: datetime | None = None
