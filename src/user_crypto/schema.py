import uuid

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
class UserCryptoBase(BaseModel):
    amount: float
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class UserCryptoCreate(UserCryptoBase):
    # ! Relations
    wallet_id: uuid.UUID
    crypto_id: uuid.UUID


# ---------------------------------------------------------------------------
class UserCryptoUpdate(BaseModel):
    amount: float
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
class UserCryptoRead(UserCryptoBase):
    id: uuid.UUID

    # ! Relations
    wallet_id: uuid.UUID
    crypto_id: uuid.UUID
