from uuid import UUID
from pydantic import BaseModel, ConfigDict, conint

from src.band_card.schemas import BankCardRead


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
