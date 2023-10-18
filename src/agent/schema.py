import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.contract.schema import ContractRead
from src.schema import IDRequest
from src.transaction.models import TransactionValueType
from src.user.schema import UserRead


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
    profit_rate: float

    created_at: datetime
    updated_at: datetime | None

    # ! Relation
    user: UserRead
    contract: ContractRead | None = None


# ---------------------------------------------------------------------------
class AgentFilterOrderFild(Enum):
    profit_rate = "profit_rate"
    is_main = "is_main"


# ---------------------------------------------------------------------------
class AgentFilterOrderBy(BaseModel):
    desc: list[AgentFilterOrderFild] = []
    asc: list[AgentFilterOrderFild] = []


# ---------------------------------------------------------------------------
class AgentFilter(BaseModel):
    is_main: None | bool = None
    order_by: AgentFilterOrderBy | None = None


# ---------------------------------------------------------------------------
class IncomeFromUser(BaseModel):
    type: TransactionValueType
    value: int
