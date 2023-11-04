import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class NewsBase(BaseModel):
    title: str
    text: str
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class NewsCreate(NewsBase):
    pass


# ---------------------------------------------------------------------------
class NewsUpdate(BaseModel):
    where: IDRequest
    data: NewsBase
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class NewsRead(NewsBase):
    id: uuid.UUID


# ---------------------------------------------------------------------------
class NewsShortRead(BaseModel):
    id: uuid.UUID
    title: str
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class NewsFilterOrderFild(Enum):
    title = "title"


# ---------------------------------------------------------------------------
class NewsFilterOrderBy(BaseModel):
    desc: list[NewsFilterOrderFild] = []
    asc: list[NewsFilterOrderFild] = []


# ---------------------------------------------------------------------------
class NewsFilter(BaseModel):
    title: str | None = None
    order_by: NewsFilterOrderBy | None = None
