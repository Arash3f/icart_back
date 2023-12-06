from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.user.models import User


# ---------------------------------------------------------------------------
class DeleteResponse(BaseModel):
    result: str


# ---------------------------------------------------------------------------
class IDRequest(BaseModel):
    id: UUID


# ---------------------------------------------------------------------------
class UserIDRequest(BaseModel):
    user_id: UUID


# ---------------------------------------------------------------------------
class ResultResponse(BaseModel):
    result: str


# ---------------------------------------------------------------------------
class UserNameInfo(BaseModel):
    first_name: str
    last_name: str
    father_name: str


# ---------------------------------------------------------------------------
class VerifyUserDep(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    is_valid: bool | None = None
    user: User | None = None


# ---------------------------------------------------------------------------
class Duration(BaseModel):
    start_date: date
    end_date: date


# ---------------------------------------------------------------------------
class ChartFilterInput(BaseModel):
    duration: Duration
    unit: int


# ---------------------------------------------------------------------------
class ChartResponse(BaseModel):
    duration: Duration
    value: int


# ---------------------------------------------------------------------------
class ChartTypeResponse(BaseModel):
    duration: Duration
    value: int
    type: str


# ---------------------------------------------------------------------------
class UpdateActivityData(BaseModel):
    is_active: bool


# ---------------------------------------------------------------------------
class UpdateActivityRequest(BaseModel):
    where: IDRequest
    data: UpdateActivityData
