import uuid

from pydantic import BaseModel, ConfigDict

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class CryptoBase(BaseModel):
    name: str
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CryptoCreate(CryptoBase):
    pass


# ---------------------------------------------------------------------------
class CryptoUpdate(BaseModel):
    where: IDRequest
    data: CryptoBase
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class CryptoRead(CryptoBase):
    id: uuid.UUID
