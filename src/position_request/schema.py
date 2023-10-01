import uuid

from pydantic import BaseModel, ConfigDict

from src.auth.schema import UserBase
from src.contract.schema import ContractBase
from src.location.schema import LocationBase
from src.position_request.models import (
    PositionRequestStatusType,
    PositionRequestType,
)


# ---------------------------------------------------------------------------
class PositionRequestBase(BaseModel):
    is_approve: bool
    target_position: PositionRequestType
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class PositionRequestCreate(BaseModel):
    requester_user_name: str | None = None
    target_position: PositionRequestType
    # contract: ContractCreate
    location_id: uuid.UUID


# ---------------------------------------------------------------------------
class PositionRequestRead(PositionRequestBase):
    id: uuid.UUID
    status: PositionRequestStatusType

    # ! Relations
    requester_user: UserBase
    next_approve_user: UserBase | None
    contract: ContractBase
    location: LocationBase
    creator: UserBase
