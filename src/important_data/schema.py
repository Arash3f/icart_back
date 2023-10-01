from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class ImportantDataBase(BaseModel):
    registration_fee: int
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class ImportantDataUpdate(BaseModel):
    where: IDRequest
    data: ImportantDataBase
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class ImportantDataRead(ImportantDataBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
class ImportantDataCreate(ImportantDataBase):
    pass
