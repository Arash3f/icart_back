from uuid import UUID

from pydantic import BaseModel

from src.schema import IDRequest


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
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role_name: str
    is_valid: bool


# ---------------------------------------------------------------------------
class UserRegisterIn(BaseModel):
    first_name: str
    last_name: str
    password: str
    national_code: str
    phone_number: str
    phone_verify_code: int
    birth_date: str


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


# ---------------------------------------------------------------------------
class ForgetPasswordIn(BaseModel):
    phone_number: str
    national_code: str
    password: str
    code: int


# ---------------------------------------------------------------------------
class UpdateUserValidationData(BaseModel):
    is_valid: bool


# ---------------------------------------------------------------------------
class UpdateUserValidationRequest(BaseModel):
    where: IDRequest
    data: UpdateUserValidationData
