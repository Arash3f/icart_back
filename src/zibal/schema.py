from pydantic import BaseModel


# ---------------------------------------------------------------------------
class ZibalCashChargingRequest(BaseModel):
    amount: int


# ---------------------------------------------------------------------------
class ZibalCashChargingRequestResponse(BaseModel):
    track_id: str


# ---------------------------------------------------------------------------
class ZibalVerifyInput(BaseModel):
    track_id: str
