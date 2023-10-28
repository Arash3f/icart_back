from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, conlist, constr

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
    password: constr(min_length=4, max_length=4)
    re_password: constr(min_length=4, max_length=4)
    new_password: constr(min_length=4, max_length=4)


# ---------------------------------------------------------------------------
class CreateCard(CardBase):
    password: constr(min_length=4, max_length=4)

    wallet_id: UUID


# ---------------------------------------------------------------------------
class CardPasswordInput(BaseModel):
    number: str


# ---------------------------------------------------------------------------
class CardUpdatePassword(BaseModel):
    where: CardPasswordInput
    data: CardUpdatePasswordData


# ---------------------------------------------------------------------------
class CardRead(CardBase):
    id: UUID

    created_at: datetime


# ---------------------------------------------------------------------------
class CardDynamicPasswordOutput(BaseModel):
    dynamic_password: constr(min_length=6, max_length=6)
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


# ---------------------------------------------------------------------------
class BuyCardResponse(BaseModel):
    card_number: str
    password: conlist(str, min_length=4, max_length=4)
