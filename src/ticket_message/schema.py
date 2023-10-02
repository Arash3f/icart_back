import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.ticket_message.models import TicketMessagePosition


# ---------------------------------------------------------------------------
class TicketMessageBase(BaseModel):
    text: str
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class TicketMessageCreate(TicketMessageBase):
    # ! Relations
    ticket_id: uuid.UUID


# ---------------------------------------------------------------------------
class TicketMessageUpdate(TicketMessageBase):
    user_status: bool
    supporter_status: bool


# ---------------------------------------------------------------------------
class TicketMessageInDB(TicketMessageCreate):
    type: TicketMessagePosition
    user_status: bool
    supporter_status: bool

    # ! Relations
    creator_id: uuid.UUID


# ---------------------------------------------------------------------------
class TicketMessageRead(TicketMessageBase):
    id: uuid.UUID
    type: TicketMessagePosition
    user_status: bool
    supporter_status: bool

    created_at: datetime

    # ! Relations
    creator_id: uuid.UUID
    ticket_id: uuid.UUID
