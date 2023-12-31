import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class LocationBase(BaseModel):
    name: str
    model_config = ConfigDict(extra="forbid")

    # ! Relations
    parent_id: uuid.UUID | None = None


# ---------------------------------------------------------------------------
class LocationCreate(LocationBase):
    pass


# ---------------------------------------------------------------------------
class LocationUpdate(BaseModel):
    where: IDRequest
    data: LocationBase
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class LocationRead(LocationBase):
    id: uuid.UUID

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class LocationInitCreate(LocationBase):
    name: str
    parent_name: str | None = None


# ---------------------------------------------------------------------------
class LocationFilter(BaseModel):
    return_all: bool | None = None
    is_main: None | bool = None
