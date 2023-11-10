import uuid
from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, conint

from src.schema import IDRequest
from src.ticket.models import TicketPosition, TicketType
from src.ticket_message.schema import TicketMessageRead
from src.user.schema import WalletCardRead


# ---------------------------------------------------------------------------
class TicketBase(BaseModel):
    title: str
    importance: conint(ge=1, le=4) = 1
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
class TicketReadV2(BaseModel):
    id: uuid.UUID
    title: str
    position: TicketPosition
    type: TicketType
    unread_user: int | None = None
    unread_supporter: int | None = None

    updated_at: datetime | None
    created_at: datetime | None


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


# ---------------------------------------------------------------------------
class _UserRead(BaseModel):
    id: UUID
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    national_code: str

    # ! Relation
    wallet: WalletCardRead


# ---------------------------------------------------------------------------
class TicketComplexRead(TicketBase):
    id: uuid.UUID
    position: TicketPosition
    number: int

    created_at: datetime
    updated_at: datetime | None

    # ! Relations
    creator: _UserRead
    messages: List[TicketMessageRead]


# ---------------------------------------------------------------------------
class TicketFilterOrderFild(Enum):
    type = "type"
    position = "position"
    important = "important"
    number = "number"


# ---------------------------------------------------------------------------
class TicketFilterOrderBy(BaseModel):
    desc: list[TicketFilterOrderFild] = []
    asc: list[TicketFilterOrderFild] = []


# ---------------------------------------------------------------------------
class TicketFilter(BaseModel):
    type: None | TicketType = None
    admin_visited: bool = False
    waiting_for_reply: bool = False
    position: None | TicketPosition = None
    important: None | int = None
    number: None | int = None
    gt_created_date: datetime | None = None
    lt_created_date: datetime | None = None
    order_by: TicketFilterOrderBy | None = None


# ---------------------------------------------------------------------------
class TicketInfo(BaseModel):
    waiting_for_reply: int = 0
    open: int = 0
    admin_visited: int = 0
    closed: int = 0
