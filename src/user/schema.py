from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.cash.schema import CashBase
from src.credit.schema import CreditBase
from src.role.schema import RoleRead


# ---------------------------------------------------------------------------
class UserBase(BaseModel):
    username: str


# ---------------------------------------------------------------------------
class UserRead(UserBase):
    id: UUID
    is_active: bool
    first_name: str | None
    last_name: str | None
    subscribe_newsletter: bool | None


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
