import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class ContractBase(BaseModel):
    number: str
    name: str | None = None
    signatory_name: str | None = None
    signatory_position: str | None = None
    employees_number: int | None = None
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class ContractCreate(ContractBase):
    file_version_id: str | None = None
    file_name: str | None = None


# ---------------------------------------------------------------------------
class ContractRead(ContractBase):
    id: uuid.UUID

    created_at: datetime
    updated_at: datetime | None

    # ! Relation
    position_request_id: uuid.UUID
