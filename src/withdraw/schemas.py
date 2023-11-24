import enum
from uuid import UUID
from pydantic import BaseModel, ConfigDict, conint

from src.band_card.schemas import BankCardRead
from src.schema import IDRequest


# ---------------------------------------------------------------------------
class WithdrawBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: conint(ge=0)


# ---------------------------------------------------------------------------
class WithdrawCreate(WithdrawBase):
    bank_card_id: UUID


# ---------------------------------------------------------------------------
class WithdrawInDB(WithdrawCreate):
    is_done: bool = False


# ---------------------------------------------------------------------------
class WithdrawUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: conint(le=0) | None = None
    bank_card_id: UUID | None = None


# ---------------------------------------------------------------------------
class WithdrawRead(WithdrawInDB):
    id: UUID


# ---------------------------------------------------------------------------
class WithdrawReadWithBankInfo(WithdrawRead):
    bank: BankCardRead


# ---------------------------------------------------------------------------
class ValidateData(WithdrawRead):
    is_valid: bool


# ---------------------------------------------------------------------------
class ValidateInput(BaseModel):
    where: IDRequest
    data: ValidateData


# ---------------------------------------------------------------------------
class WithdrawFilterOrderFild(enum.Enum):
    is_done = "is_done"
    is_verified = "is_verified"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class WithdrawFilterOrderBy(BaseModel):
    desc: list[WithdrawFilterOrderFild] = []
    asc: list[WithdrawFilterOrderFild] = []


# ---------------------------------------------------------------------------
class WithdrawFilter(BaseModel):
    is_done: None | bool = None
    is_verified: None | bool = None
    order_by: WithdrawFilterOrderBy | None = None
