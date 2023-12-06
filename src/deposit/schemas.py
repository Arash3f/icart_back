from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, conint


# ---------------------------------------------------------------------------
class DepositBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: conint(ge=0)
    zibal_track_id: str
    wallet_id: UUID


# ---------------------------------------------------------------------------
class DepositApprove(BaseModel):
    track_id: str
    card_number: str


# ---------------------------------------------------------------------------
class DepositCreate(DepositBase):
    pass


# ---------------------------------------------------------------------------
class DepositRead(DepositBase):
    id: UUID

    updated_at: datetime | None
    created_at: datetime | None


# ---------------------------------------------------------------------------
class DepositFilter(BaseModel):
    wallet_id: None | bool = None
    zibal_track_id: None | str = None
