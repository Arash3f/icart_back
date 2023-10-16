import uuid
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.contract.schema import ContractBase
from src.location.schema import LocationRead
from src.role.schema import RoleBase


# ---------------------------------------------------------------------------
class OrganizationBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None


# ---------------------------------------------------------------------------
class UserRead(BaseModel):
    id: uuid.UUID
    username: str
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    location: LocationRead | None
    national_code: str
    model_config = ConfigDict(extra="forbid")

    # ! Relations
    role: RoleBase


# ---------------------------------------------------------------------------
class OrganizationRead(BaseModel):
    id: uuid.UUID
    model_config = ConfigDict(extra="forbid")

    # # ! Relation
    contract: ContractBase | None = None
    user: UserRead
    location: LocationRead | None = None


# ---------------------------------------------------------------------------
class OrganizationReadWithUser(OrganizationRead):
    user: UserRead


# ---------------------------------------------------------------------------
class OrganizationFilterOrderFild(Enum):
    agent_id = "agent_id"


# ---------------------------------------------------------------------------
class OrganizationFilterOrderBy(BaseModel):
    desc: list[OrganizationFilterOrderFild] = []
    asc: list[OrganizationFilterOrderFild] = []


# ---------------------------------------------------------------------------
class OrganizationFilter(BaseModel):
    location_id: None | UUID = None
    user_id: None | UUID = None
    agent_id: None | UUID = None
    order_by: OrganizationFilterOrderBy | None = None
