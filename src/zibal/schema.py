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


# ---------------------------------------------------------------------------
class NationalIdentityInquiryInput(BaseModel):
    national_code: str
    birth_date: str


# ---------------------------------------------------------------------------
class NationalIdentityInquiryOutput(BaseModel):
    matched: bool
    lastName: str
    fatherName: str
    firstName: str
    nationalCode: str
    isDead: bool
    alive: bool
