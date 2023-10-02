import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.location.schema import LocationRead


# ---------------------------------------------------------------------------
class OrganizationBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None


# ---------------------------------------------------------------------------
class UserRead(BaseModel):
    user_name: str
    id: uuid.UUID
    active: bool
    validation: bool
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    notify_transaction: bool | None
    subscribe_newsletter: bool | None


# ---------------------------------------------------------------------------
class OrganizationRead(OrganizationBase):
    id: uuid.UUID

    created_at: datetime
    updated_at: datetime | None
    contract_number: str | None = None
    signatory_name:str | None = None
    signatory_position: str | None = None
    employees_number: str | None = None

    address: str | None = None
    # ! Relation
    location: LocationRead


# ---------------------------------------------------------------------------
class OrganizationReadWithUser(OrganizationRead):
    user_organization: UserRead