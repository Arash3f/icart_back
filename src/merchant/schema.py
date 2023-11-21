from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, confloat

from src.contract.schema import ContractRead, ContractShortInfo, ContractReadV2
from src.location.schema import LocationRead
from src.position_request.models import FieldOfWorkType, SellingType
from src.schema import IDRequest
from src.user.schema import UserRead


# ---------------------------------------------------------------------------
class MerchantBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    number: str
    field_of_work: FieldOfWorkType | None
    geo: str | None
    selling_type: SellingType

    blue_profit: confloat(ge=0, le=100) = 0.0
    silver_profit: confloat(ge=0, le=100) = 0.0
    gold_profit: confloat(ge=0, le=100) = 0.0
    corporate_profit: confloat(ge=0, le=100) = 0.0


# ---------------------------------------------------------------------------
class MerchantRead(MerchantBase):
    id: UUID
    is_active: bool

    created_at: datetime
    updated_at: datetime | None

    # # ! Relation
    contract: ContractRead | None = None
    user: UserRead
    location: LocationRead | None = None


# ---------------------------------------------------------------------------
class MerchantReadV2(MerchantBase):
    id: UUID

    field_of_work: FieldOfWorkType | None
    geo: str | None
    selling_type: SellingType

    blue_profit: confloat(ge=0, le=100) = 0.0
    silver_profit: confloat(ge=0, le=100) = 0.0
    gold_profit: confloat(ge=0, le=100) = 0.0
    corporate_profit: confloat(ge=0, le=100) = 0.0

    # # ! Relation
    contract: ContractReadV2 | None = None
    location: LocationRead | None = None


# ---------------------------------------------------------------------------
class StoresRead(MerchantBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None

    # # ! Relation
    user: UserRead
    contract: ContractShortInfo | None = None
    location: LocationRead | None = None


# ---------------------------------------------------------------------------
class MerchantUpdateData(BaseModel):
    blue_profit: confloat(ge=0, le=100) = 0.0
    silver_profit: confloat(ge=0, le=100) = 0.0
    gold_profit: confloat(ge=0, le=100) = 0.0
    corporate_profit: confloat(ge=0, le=100) = 0.0


# ---------------------------------------------------------------------------
class MerchantUpdate(BaseModel):
    where: IDRequest
    data: MerchantUpdateData


# ---------------------------------------------------------------------------
class MerchantFilterOrderFild(Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    best_sellers = "best_sellers"


# ---------------------------------------------------------------------------
class MerchantFilterOrderBy(BaseModel):
    desc: list[MerchantFilterOrderFild] = []
    asc: list[MerchantFilterOrderFild] = []


# ---------------------------------------------------------------------------
class MerchantFilter(BaseModel):
    name: None | str = None
    national_code: None | str = None
    location_id: None | UUID = None
    user_id: None | UUID = None
    agent_id: None | UUID = None
    selling_type: None | SellingType = None
    is_active: None | bool = None
    field_of_work: None | FieldOfWorkType = None
    order_by: MerchantFilterOrderBy | None = None


# ---------------------------------------------------------------------------
class MerchantAggregateRead(BaseModel):
    count: int
    field_of_work: FieldOfWorkType
