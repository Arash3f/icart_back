import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.auth.schema import UserBase
from src.log.models import LogType


# ---------------------------------------------------------------------------
class LogBase(BaseModel):
    detail: str | None = None
    type: LogType | None = None
    model_config = ConfigDict(extra="forbid")

    # ! Relations
    user_id: uuid.UUID | None = None


# ---------------------------------------------------------------------------
class LogCreate(LogBase):
    pass


# ---------------------------------------------------------------------------
class LogRead(LogBase):
    id: uuid.UUID

    created_at: datetime
    updated_at: datetime | None

    # ! Relation
    user: UserBase | None = None


# ---------------------------------------------------------------------------
class LogFilterOrderFild(Enum):
    type = "type"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class LogFilterOrderBy(BaseModel):
    desc: list[LogFilterOrderFild] = []
    asc: list[LogFilterOrderFild] = []


# ---------------------------------------------------------------------------
class LogFilter(BaseModel):
    name: None | str = None
    national_code: None | str = None
    type: LogType | None = None
    order_by: LogFilterOrderBy | None = None
