import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class LocationBase(BaseModel):
    name: str
    model_config = ConfigDict(extra="forbid")

    # ! Relations
    parent_id: uuid.UUID | None = None


# ---------------------------------------------------------------------------
class LocationBaseV2(BaseModel):
    id: UUID
    name: str
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class LocationComplex(BaseModel):
    name: str
    model_config = ConfigDict(extra="forbid")

    # ! Relations
    parent: LocationBase | None = None


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
class LocationCompleteRead(BaseModel):
    id: uuid.UUID
    name: str
    model_config = ConfigDict(extra="forbid")

    # ! Relations
    children: list[LocationBaseV2] = []

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class LocationInitCreate(LocationBase):
    name: str
    parent_name: str | None = None


# ---------------------------------------------------------------------------
class LocationFilterOrderFild(Enum):
    is_main = "is_main"
    name = "name"
    parent_id = "parent_id"
    created_at = "created_at"
    updated_at = "updated_at"


# ---------------------------------------------------------------------------
class LocationFilterOrderBy(BaseModel):
    desc: list[LocationFilterOrderFild] = []
    asc: list[LocationFilterOrderFild] = []


# ---------------------------------------------------------------------------
class LocationFilter(BaseModel):
    is_main: None | bool = None
    parent_id: None | UUID = None
    name: None | str = None
    order_by: LocationFilterOrderBy | None = None
