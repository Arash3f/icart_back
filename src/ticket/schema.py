import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, conint

from src.schema import IDRequest
from src.ticket.models import TicketPosition, TicketType
from src.ticket_message.schema import TicketMessageRead


# ---------------------------------------------------------------------------
class TicketBase(BaseModel):
    title: str
    importance: conint(ge=1, le=4)
    type: TicketType
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class TicketCreateData(BaseModel):
    ticket: TicketBase
    text: str


# ---------------------------------------------------------------------------
class TicketCreate(TicketBase):
    number: int

    # ! Relations
    creator_id: uuid.UUID


# ---------------------------------------------------------------------------
class TicketUpdateDataBaseModel(BaseModel):
    position: TicketPosition


# ---------------------------------------------------------------------------
class TicketUpdate(BaseModel):
    where: IDRequest
    data: TicketUpdateDataBaseModel
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class TicketRead(TicketBase):
    id: uuid.UUID
    position: TicketPosition
    number: int

    created_at: datetime
    updated_at: datetime | None

    # ! Relations
    creator_id: uuid.UUID
    messages: List[TicketMessageRead]
