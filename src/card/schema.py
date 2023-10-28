from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.card.models import CardEnum
from src.schema import IDRequest


# ---------------------------------------------------------------------------
class CardBase(BaseModel):
    number: str
    cvv2: int
    expiration_at: datetime | None = None
    type: CardEnum

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class BuyCard(BaseModel):
    type: CardEnum


# ---------------------------------------------------------------------------
class CardUpdatePasswordData(BaseModel):
    password: str
    re_password: str
    new_password: str


# ---------------------------------------------------------------------------
class CreateCard(CardBase):
    password: str

    wallet_id: UUID


# ---------------------------------------------------------------------------
class CardUpdatePassword(BaseModel):
    where: IDRequest
    data: CardUpdatePasswordData


# ---------------------------------------------------------------------------
class CardRead(CardBase):
    id: UUID

    created_at: datetime


# ---------------------------------------------------------------------------
class CardDynamicPasswordOutput(BaseModel):
    dynamic_password: int
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CardDynamicPasswordInput(BaseModel):
    number: str


# ---------------------------------------------------------------------------
class CardFilterOrderFild(Enum):
    number = "number"


# ---------------------------------------------------------------------------
class CardFilterOrderBy(BaseModel):
    desc: list[CardFilterOrderFild] = []
    asc: list[CardFilterOrderFild] = []


# ---------------------------------------------------------------------------
class CardFilter(BaseModel):
    number: None | str = None
    type: None | CardEnum = None
    user_id: None | UUID = None
    order_by: CardFilterOrderBy | None = None
