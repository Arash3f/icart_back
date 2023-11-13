from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, conint, confloat

from src.fee.models import FeeTypeEnum, FeeUserType
from src.schema import IDRequest


# ---------------------------------------------------------------------------
class FeeBase(BaseModel):
    limit: int
    type: FeeTypeEnum
    user_type: FeeUserType
    percentage: confloat(ge=0, le=100) | None = None
    value: int | None = None

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
