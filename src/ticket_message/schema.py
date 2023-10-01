import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class TicketMessageBase(BaseModel):
    text: str
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class TicketMessageCreate(TicketMessageBase):
    # ! Relations
    ticket_id: uuid.UUID


# ---------------------------------------------------------------------------
class TicketMessageInDB(TicketMessageCreate):
    # ! Relations
    creator_id: uuid.UUID


# ---------------------------------------------------------------------------
class TicketMessageRead(TicketMessageBase):
    id: uuid.UUID

    created_at: datetime

    # ! Relations
    creator_id: uuid.UUID
    ticket_id: uuid.UUID
