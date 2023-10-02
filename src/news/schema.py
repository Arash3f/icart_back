import uuid

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
class NewsFilter(BaseModel):
    return_all: bool | None = None
    title: str | None | bool = None
