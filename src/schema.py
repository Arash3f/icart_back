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
class ResultResponse(BaseModel):
    result: str


# ---------------------------------------------------------------------------
class VerifyUserDep(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    is_valid: bool | None = None
    user: User | None = None
