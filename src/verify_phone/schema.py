from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.verify_phone.models import VerifyPhoneType


# ---------------------------------------------------------------------------
class VerifyPhoneBase(BaseModel):
    phone_number: str
    verify_code: int
    expiration_code_at: datetime
    type: VerifyPhoneType | None = None
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
    type = "type"
    phone_number = "phone_number"
    created_at = "created_at"


# ---------------------------------------------------------------------------
class VerifyPhoneFilterOrderBy(BaseModel):
    desc: list[VerifyPhoneFilterOrderFild] = []
    asc: list[VerifyPhoneFilterOrderFild] = []


# ---------------------------------------------------------------------------
class VerifyPhoneFilter(BaseModel):
    phone_number: str | bool | None = None
    type: VerifyPhoneType | None = None
    order_by: VerifyPhoneFilterOrderBy | None = None
