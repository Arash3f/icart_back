from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class VerifyPhoneBase(BaseModel):
    phone_number: str
    verify_code: int
    expiration_code_at: datetime
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class VerifyPhoneRead(VerifyPhoneBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class VerifyPhoneNumberRequestIn(BaseModel):
    phone_number: str


# ---------------------------------------------------------------------------
class VerifyPhoneFilterOrderFild(Enum):
    pass


# ---------------------------------------------------------------------------
class VerifyPhoneFilterOrderBy(BaseModel):
    desc: list[VerifyPhoneFilterOrderFild] = []
    asc: list[VerifyPhoneFilterOrderFild] = []


# ---------------------------------------------------------------------------
class VerifyPhoneFilter(BaseModel):
    return_all: bool | None = None
    expiration_code_at: datetime | None | bool = None
    phone_number: str | bool | None = None
    order_by: VerifyPhoneFilterOrderBy | None = None
