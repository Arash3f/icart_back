from uuid import UUID

from pydantic import BaseModel


# ---------------------------------------------------------------------------
class UserBase(BaseModel):
    username: str
    national_code: str
    first_name: str | None = None
    last_name: str | None = None


# ---------------------------------------------------------------------------
class AccessToken(BaseModel):
    access_token: str
    token_type: str


# ---------------------------------------------------------------------------
class UserRegisterIn(BaseModel):
    first_name: str
    last_name: str
    password: str
    national_code: str
    phone_number: str
    phone_verify_code: int


# ---------------------------------------------------------------------------
class OneTimePasswordRequestIn(BaseModel):
    username: str


# ---------------------------------------------------------------------------
class VerifyUsernameAndNationalCode(BaseModel):
    username: str
    national_code: str


# ---------------------------------------------------------------------------
class UserInDB(UserBase):
    password: str
    role_id: UUID
