import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class UserMessageBase(BaseModel):
    title: str
    text: str
    model_config = ConfigDict(extra="forbid")

    # ! Relations
    user_id: uuid.UUID


# ---------------------------------------------------------------------------
class UserMessageCreate(UserMessageBase):
    pass


# ---------------------------------------------------------------------------
class UserMessageUpdate(BaseModel):
    where: IDRequest
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class UserMessageRead(UserMessageBase):
    id: uuid.UUID
    status: bool


# ---------------------------------------------------------------------------
class UserMessageShortRead(BaseModel):
    id: uuid.UUID
    title: str
    status: bool
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class UserMessageFilterOrderFild(Enum):
    status = "status"
    title = "title"


# ---------------------------------------------------------------------------
class UserMessageFilterOrderBy(BaseModel):
    desc: list[UserMessageFilterOrderFild] = []
    asc: list[UserMessageFilterOrderFild] = []


# ---------------------------------------------------------------------------
class UserMessageFilter(BaseModel):
    status: bool | None = None
    title: str | None = None
    order_by: UserMessageFilterOrderBy | None = None
