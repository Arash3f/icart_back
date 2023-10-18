from uuid import UUID
from pydantic import BaseModel

from src.invoice.schema import InvoiceRead


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
