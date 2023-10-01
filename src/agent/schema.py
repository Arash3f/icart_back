import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class AgentBase(BaseModel):
    pass


# ---------------------------------------------------------------------------
class AgentUpdateData(AgentBase):
    # ! Relations
    abilities: list[UUID]


# ---------------------------------------------------------------------------
class AgentUpdate(BaseModel):
    where: IDRequest
    data: AgentUpdateData
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class AgentRead(AgentBase):
    id: uuid.UUID
    is_main: bool
    interest_rates: float

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class AgentFilterOrderFild(Enum):
    interest_rates = "interest_rates"
    is_main = "is_main"


# ---------------------------------------------------------------------------
class AgentFilterOrderBy(BaseModel):
    desc: list[AgentFilterOrderFild] = []
    asc: list[AgentFilterOrderFild] = []


# ---------------------------------------------------------------------------
class AgentFilter(BaseModel):
    return_all: bool | None = None
    is_main: None | bool = None
    order_by: AgentFilterOrderBy | None = None
