import uuid
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.contract.schema import ContractBase, ContractRead
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
    is_active: bool
    model_config = ConfigDict(extra="forbid")

    # ! Relations
    role: RoleBase


# ---------------------------------------------------------------------------
class OrganizationRead(BaseModel):
    id: uuid.UUID
    is_active: bool
    model_config = ConfigDict(extra="forbid")

    # # ! Relation
    contract: ContractRead | None = None
    user: UserRead
    location: LocationRead | None = None


# ---------------------------------------------------------------------------
class OrganizationPublicRead(BaseModel):
    id: uuid.UUID
    name: str
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class OrganizationPublicResponse(BaseModel):
    count: int
    list: list[OrganizationPublicRead]


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
    name: None | str = None
    national_code: None | str = None
    location_id: None | UUID = None
    user_id: None | UUID = None
    agent_id: None | UUID = None
    is_active: None | bool = None
    order_by: OrganizationFilterOrderBy | None = None


# ---------------------------------------------------------------------------
class OrganizationGenerateUser(BaseModel):
    name: str
    last_name: str
    national_code: str
    phone_number: str
    father_name: str
    birth_place: str
    location_id: UUID
    postal_code: str
    tel: str
    address: str
    considered_credit: int
    personnel_number: str | None = None
    organizational_section: str | None = None
    job_class: str | None = None


# ---------------------------------------------------------------------------
class OrganizationAppendUser(BaseModel):
    national_code: str
    phone_number: str
    considered_credit: int
