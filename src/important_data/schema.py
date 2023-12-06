from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, confloat

from src.schema import IDRequest


# ---------------------------------------------------------------------------
class ImportantDataBase(BaseModel):
    registration_fee: int
    blue_card_cost: int | None = None
    icart_members: int
    referral_user_number: int
    referral_transactions: int
    referral_transaction_percentage: confloat(ge=0, le=100) | None = None
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


# ---------------------------------------------------------------------------
class SystemAdditionalInfo(BaseModel):
    agent_count: int = 0
    organization_count: int = 0
    merchant_count: int = 0
    user_count: int = 0
    sales_agent_count: int = 0


# ---------------------------------------------------------------------------
class SystemRequestInfo(BaseModel):
    new_agent_count: int = 0
    new_organization_count: int = 0
    new_merchant_count: int = 0
    new_user_count: int = 0
    new_sales_agent_count: int = 0
