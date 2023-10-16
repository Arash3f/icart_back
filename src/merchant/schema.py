from datetime import datetime
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
