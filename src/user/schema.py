from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from src.card.schema import CardRead
from src.cash.schema import CashBase, CashBalanceResponse
from src.credit.schema import CreditBase, CreditBalanceResponse
from src.location.schema import LocationRead, LocationComplex
from src.role.schema import RoleRead, RoleBase
from src.schema import IDRequest


class WalletCardRead(BaseModel):
    id: UUID

    # ! relations
    cards: list[CardRead] = []


# ---------------------------------------------------------------------------
class UserBase(BaseModel):
    username: str


# ---------------------------------------------------------------------------
class UserReadV2(BaseModel):
    username: str
    first_name: str | None
    last_name: str | None


# ---------------------------------------------------------------------------
class UserRead(UserBase):
    id: UUID
    username: str
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    national_code: str
    is_active: bool
    is_valid: bool

    # ! Relation
    role: RoleBase
    location: LocationRead | None


# ---------------------------------------------------------------------------
class UserRead2(UserBase):
    id: UUID
    username: str
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    national_code: str
    tel: str | None = None
    postal_code: str | None = None
    father_name: str | None = None
    birth_place: str | None = None
    address: str | None = None
    is_active: bool
    is_valid: bool

    # ! Relation
    wallet: WalletCardRead
    role: RoleBase
    location: LocationComplex | None


# ---------------------------------------------------------------------------
class UserCreditCashRead(BaseModel):
    id: UUID

    # ! Relation
    credit: CreditBase
    cash: CashBase


# ---------------------------------------------------------------------------
class CreateUser(BaseModel):
    username: str
    password: str


# ---------------------------------------------------------------------------
class UserReadWithRole(UserRead):
    role: RoleRead

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class UserMeResponse(UserRead):
    role: RoleRead
    cash: CashBalanceResponse
    credit: CreditBalanceResponse

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class UserFilterOrderFild(Enum):
    national_code = "national_code"
    phone_number = "phone_number"
    first_name = "first_name"
    last_name = "last_name"
    is_active = "is_active"
    is_valid = "is_valid"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class UserFilterOrderBy(BaseModel):
    desc: list[UserFilterOrderFild] = []
    asc: list[UserFilterOrderFild] = []


# ---------------------------------------------------------------------------
class UserFilter(BaseModel):
    national_code: None | str = None
    phone_number: None | str = None
    name: str | None = None
    is_active: bool | None = None
    is_valid: bool | None = None
    father_name: str | None = None
    tel: str | None = None
    location_id: UUID | None = None
    order_by: UserFilterOrderBy | None = None


# ---------------------------------------------------------------------------
class UpdateUserData(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    birth_place: str | None = None
    postal_code: str | None = None
    father_name: str | None = None
    tel: str | None = None
    address: str | None = None
    location_id: UUID | None = None


# ---------------------------------------------------------------------------
class UpdateUserRequest(BaseModel):
    where: IDRequest
    data: UpdateUserData


# ---------------------------------------------------------------------------
class UpdateUserActivityData(BaseModel):
    is_active: bool


# ---------------------------------------------------------------------------
class UpdateUserActivityRequest(BaseModel):
    where: IDRequest
    data: UpdateUserActivityData


# ---------------------------------------------------------------------------
class UserRoleUpdateInput(BaseModel):
    role_id: UUID


# ---------------------------------------------------------------------------
class UserRoleUpdate(BaseModel):
    where: IDRequest
    data: UserRoleUpdateInput
