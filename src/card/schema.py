from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, constr

from src.card.models import CardEnum
from src.location.schema import LocationComplex, LocationBase


# ---------------------------------------------------------------------------
class UserReadV2(BaseModel):
    username: str
    first_name: str | None
    last_name: str | None


# ---------------------------------------------------------------------------
class WalletReadV2(BaseModel):
    user: UserReadV2 | None = None


# ---------------------------------------------------------------------------
class UserReadV3(BaseModel):
    username: str
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    national_code: str
    tel: str | None = None
    father_name: str | None = None
    address: str | None = None
    postal_code: str | None = None
    location: LocationBase | None


class WalletReadV3(BaseModel):
    user: UserReadV3 | None = None


# ---------------------------------------------------------------------------
class CardBase(BaseModel):
    number: str
    cvv2: int
    expiration_at: str | datetime | None = None
    type: CardEnum

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CardUpdatePasswordData(BaseModel):
    forget_password: constr(min_length=4, max_length=4)
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

    wallet: WalletReadV3
    created_at: datetime


# ---------------------------------------------------------------------------
class CardReadV2(BaseModel):
    id: UUID
    number: str
    wallet: WalletReadV2


# ---------------------------------------------------------------------------
class CardDynamicPasswordOutput(BaseModel):
    dynamic_password: constr(min_length=6, max_length=6)
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CardDynamicPasswordInput(BaseModel):
    number: str


# ---------------------------------------------------------------------------
class CardForgetPasswordInput(BaseModel):
    number: str


# ---------------------------------------------------------------------------
class CardFilterOrderFild(Enum):
    number = "number"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class CardFilterOrderBy(BaseModel):
    desc: list[CardFilterOrderFild] = []
    asc: list[CardFilterOrderFild] = []


# ---------------------------------------------------------------------------
class CardFilter(BaseModel):
    name: None | str = None
    last_name: None | str = None
    national_code: None | str = None
    number: None | str = None
    type: None | CardEnum = None
    user_id: None | UUID = None
    is_receive: None | bool = None
    order_by: CardFilterOrderBy | None = None


# ---------------------------------------------------------------------------
class CardToCardInput(BaseModel):
    receiver_card_number: str
    transferor_card_number: str
    amount: int
    dynamic_password: constr(min_length=6, max_length=6)


# ---------------------------------------------------------------------------
class ConfirmCardReceive(BaseModel):
    card_number: str
    password: constr(min_length=4, max_length=4)


# ---------------------------------------------------------------------------
class ReferralCode(BaseModel):
    referral_code: str
