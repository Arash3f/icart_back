from uuid import UUID

from pydantic import BaseModel


# ---------------------------------------------------------------------------
class ZibalCashChargingVerify(BaseModel):
    zibal_track_id: str


# ---------------------------------------------------------------------------
class ZibalCashChargingRequest(BaseModel):
    amount: int
