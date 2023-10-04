import uuid

from pydantic import BaseModel, ConfigDict

from src.contract.schema import ContractBase
from src.location.schema import LocationRead


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
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class OrganizationRead(BaseModel):
    id: uuid.UUID
    model_config = ConfigDict(extra="forbid")

    # # ! Relation
    contract: ContractBase | None = None
    user_organization: UserRead
    location: LocationRead


# ---------------------------------------------------------------------------
class OrganizationReadWithUser(OrganizationRead):
    user_organization: UserRead
