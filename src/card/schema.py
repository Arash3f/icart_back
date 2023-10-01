from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.card.models import CardEnum
from src.schema import IDRequest


# ---------------------------------------------------------------------------
class CardBase(BaseModel):
    number: str
    cvv2: int
    dynamic_password: int | None
    expiration_at: datetime
    dynamic_password_exp: datetime | None
    type: CardEnum

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CardUpdatePasswordData(BaseModel):
    password: str
    re_password: str
    new_password: str


# ---------------------------------------------------------------------------
class CardUpdatePassword(BaseModel):
    where: IDRequest
    data: CardUpdatePasswordData


# ---------------------------------------------------------------------------
class CardRead(CardBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class BalanceRead(BaseModel):
    number: str
    balance: int


# ---------------------------------------------------------------------------
class CardDynamicPasswordOutput(BaseModel):
    dynamic_password: int
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CardDynamicPasswordInput(BaseModel):
    number: str
