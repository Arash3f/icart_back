from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, conint

from src.fee.models import FeeTypeEnum
from src.schema import IDRequest


# ---------------------------------------------------------------------------
class FeeBase(BaseModel):
    limit: int
    percentage: conint(ge=0, le=100) | None = None
    value: int | None = None
    value_limit: int
    type: FeeTypeEnum

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class FeeCreate(FeeBase):
    pass


# ---------------------------------------------------------------------------
class FeeUpdate(BaseModel):
    where: IDRequest
    data: FeeBase


# ---------------------------------------------------------------------------
class FeeRead(FeeBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None
