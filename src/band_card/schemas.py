import enum
from uuid import UUID
from pydantic import BaseModel
from pydantic_extra_types.payment import PaymentCardNumber


# --------------------------------------------------------
class BankCardBase(BaseModel):
    card_number: PaymentCardNumber
    shaba_number: str


# --------------------------------------------------------
class BankCardCreate(BankCardBase):
    pass


# --------------------------------------------------------
class BankCardUpdate(BankCardBase):
    pass


# --------------------------------------------------------
class BankCardRead(BankCardBase):
    id: UUID


# ---------------------------------------------------------------------------
class BankCardFilterOrderFild(enum.Enum):
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class BankCardFilterOrderBy(BaseModel):
    desc: list[BankCardFilterOrderFild] = []
    asc: list[BankCardFilterOrderFild] = []


# ---------------------------------------------------------------------------
class BankCardFilter(BaseModel):
    card_number: None | bool = None
    shaba_number: None | bool = None
    name: None | str = None
    last_name: None | str = None
    national_code: None | str = None
    order_by: BankCardFilterOrderBy | None = None
