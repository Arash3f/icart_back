from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.contract.schema import ContractBase
from src.location.schema import LocationRead
from src.position_request.models import FieldOfWorkType, SellingType
from src.user.schema import UserRead


# ---------------------------------------------------------------------------
class MerchantBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    number: str
    field_of_work: FieldOfWorkType | None
    selling_type: SellingType


# ---------------------------------------------------------------------------
class MerchantRead(MerchantBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None

    # # ! Relation
    contract: ContractBase | None = None
    user: UserRead
    location: LocationRead | None = None


# ---------------------------------------------------------------------------
class MerchantFilterOrderFild(Enum):
    created_at = "created_at"
    best_sellers = "best_sellers"


# ---------------------------------------------------------------------------
class MerchantFilterOrderBy(BaseModel):
    desc: list[MerchantFilterOrderFild] = []
    asc: list[MerchantFilterOrderFild] = []


# ---------------------------------------------------------------------------
class MerchantFilter(BaseModel):
    location_id: None | UUID = None
    selling_type: None | SellingType = None
    order_by: MerchantFilterOrderBy | None = None
