from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class PosBase(BaseModel):
    token: str

    # ! Relations
    merchant_id: UUID

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class PosCreate(PosBase):
    pass


# ---------------------------------------------------------------------------
class PosUpdate(BaseModel):
    where: IDRequest
    data: PosBase


# ---------------------------------------------------------------------------
class PosRead(PosBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None
