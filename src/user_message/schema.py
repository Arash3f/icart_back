import uuid

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
class UserMessageFilter(BaseModel):
    return_all: bool | None = None
    status: bool | None = None
