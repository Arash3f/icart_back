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
    national_code: str
    model_config = ConfigDict(extra="forbid")


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
