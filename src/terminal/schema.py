from uuid import UUID

from pydantic import BaseModel

from src.invoice.schema import InvoiceRead
from src.transaction.models import TransactionEnum


# ---------------------------------------------------------------------------
class TerminalBase(BaseModel):
    number: str
    redirect_url: str


# ---------------------------------------------------------------------------
class TerminalCreate(BaseModel):
    redirect_url: str

    # ! Relation
    invoice_number: int


# ---------------------------------------------------------------------------
class TerminalRead(TerminalBase):
    id: UUID


# ---------------------------------------------------------------------------
class TerminalVerifyOutput(TerminalBase):
    id: UUID

    # ! Relation
    invoice: InvoiceRead


# ---------------------------------------------------------------------------
class GenerateTerminalOutput(BaseModel):
    terminal_token: str


# ---------------------------------------------------------------------------
class GenerateTerminalInput(BaseModel):
    merchant_token: str
    invoice_number: int
    value: int
    type: TransactionEnum
