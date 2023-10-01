from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class AbilityBase(BaseModel):
    name: str
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class AbilityCreate(AbilityBase):
    pass


# ---------------------------------------------------------------------------
class AbilityUpdate(BaseModel):
    where: IDRequest
    data: AbilityBase
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class AbilityRead(AbilityBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class AbilityFilterOrderFild(Enum):
    name = "name"


# ---------------------------------------------------------------------------
class AbilityFilterOrderBy(BaseModel):
    desc: list[AbilityFilterOrderFild] = []
    asc: list[AbilityFilterOrderFild] = []


# ---------------------------------------------------------------------------
class AbilityFilter(BaseModel):
    return_all: bool | None = None
    name: str | None | bool = None
    order_by: AbilityFilterOrderBy | None = None
