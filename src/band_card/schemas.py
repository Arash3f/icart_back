from uuid import UUID
from pydantic import BaseModel, Field
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
