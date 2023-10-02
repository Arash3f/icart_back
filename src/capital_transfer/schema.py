import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.capital_transfer.models import CapitalTransferEnum


# ---------------------------------------------------------------------------
class CapitalTransferBase(BaseModel):
    transfer_type: CapitalTransferEnum
    value: float
    model_config = ConfigDict(extra="forbid")

    file_version_id: str | None = None
    file_name: str | None = None

    # ! Relations
    receiver_id: uuid.UUID | None = None


# ---------------------------------------------------------------------------
class CapitalTransferCreate(CapitalTransferBase):
    pass


# ---------------------------------------------------------------------------
class CapitalTransferUpdate(BaseModel):
    finish: bool
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CapitalTransferRead(CapitalTransferBase):
    id: uuid.UUID
    finish: bool

    created_at: datetime
    updated_at: datetime | None
