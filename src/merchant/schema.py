from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class MerchantBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    number: str


# ---------------------------------------------------------------------------
class MerchantRead(MerchantBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None
