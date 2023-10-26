import enum

from sqlalchemy import UUID, Boolean, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.contract.models import Contract
from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class PositionRequestType(enum.Enum):
    AGENT = "AGENT"
    ORGANIZATION = "ORGANIZATION"
    MERCHANT = "MERCHANT"


# ---------------------------------------------------------------------------
class PositionRequestStatusType(enum.Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"


# ---------------------------------------------------------------------------
class SellingType(enum.Enum):
    CASH = "CASH"
    CREDIT = "CREDIT"
    INSTALLMENT = "INSTALLMENT"
    BOTH = "BOTH"


# ---------------------------------------------------------------------------
class FieldOfWorkType(enum.Enum):
    MOBILE_STORE = "MOBILE_STORE"
    AUDIO_AND_VIDEO_PRODUCT_STORE = "AUDIO_AND_VIDEO_PRODUCT_STORE"
    KITCHEN_ACCESSORIES_STORE = "KITCHEN_ACCESSORIES_STORE"
    ELECTRICAL_APPLIANCES_STORE = "ELECTRICAL_APPLIANCES_STORE"
    SLEEP_GOODS_STORES = "SLEEP_GOODS_STORES"
    FURNITURE_STORES = "FURNITURE_STORES"
    GROCERY_STORES = "GROCERY_STORES"
    PROTEIN_STORE = "PROTEIN_STORE"
    CHANDELIERS_AND_ELECTRICAL_APPLIANCES = "CHANDELIERS_AND_ELECTRICAL_APPLIANCES"
    SUPER_MARKETS = "SUPER_MARKETS"
    BAKERY = "BAKERY"
    FRUIT_SHOPS = "FRUIT_SHOPS"
    STATIONERY_STORES = "STATIONERY_STORES"
    DTY_FRUITS_SHOP = "DTY_FRUITS_SHOP"
    DENTAL_CLINICS = "DENTAL_CLINICS"
    BEAUTY = "BEAUTY"
    MEDICAL = "MEDICAL"
    TRANSPORTATION = "TRANSPORTATION"
    CONFECTIONERY = "CONFECTIONERY"
    RESTAURANT = "RESTAURANT"
    CLOTHING_STORES = "CLOTHING_STORES"
    HAIRDRESSERS = "HAIRDRESSERS"
    LASER_CENTERS = "LASER_CENTERS"
    GOLD_AND_SILVER = "GOLD_AND_SILVER"
    WATCH_SHOP = "WATCH_SHOP"
    PERFUME_AND_COLOGNE_STORE = "PERFUME_AND_COLOGNE_STORE"
    DECORATION = "DECORATION"
    COSMETIC = "COSMETIC"
    MESON = "MESON"
    CAR_REPAIRS = "CAR_REPAIRS"
    PHARMACY = "PHARMACY"
    EDUCATIONAL_SERVICES = "EDUCATIONAL_SERVICES"
    HOME_APPLIANCES = "HOME_APPLIANCES"


# ---------------------------------------------------------------------------
class PositionRequest(Base, BaseMixin):
    __tablename__ = "position_request"

    name = Column(String, nullable=True)
    field_of_work = Column(Enum(FieldOfWorkType), nullable=True)
    postal_code = Column(String, nullable=True)
    tel = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    employee_count = Column(Integer, nullable=True)
    is_approve = Column(Boolean, default=False)
    target_position = Column(Enum(PositionRequestType))
    selling_type = Column(Enum(SellingType), nullable=True)
    received_money = Column(String, nullable=True)
    tracking_code = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    status = Column(
        Enum(PositionRequestStatusType),
        default=PositionRequestStatusType.OPEN,
    )

    # ! Relations
    contract = relationship(
        Contract,
        uselist=False,
        back_populates="position_request",
        lazy="selectin",
    )

    requester_user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    requester_user = relationship(
        "User",
        foreign_keys=[requester_user_id],
        lazy="selectin",
    )

    creator_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    creator = relationship("User", foreign_keys=[creator_id], lazy="selectin")

    next_approve_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=True,
    )
    next_approve_user = relationship(
        "User",
        foreign_keys=[next_approve_user_id],
        lazy="selectin",
    )

    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"))
    location = relationship(
        "Location",
        foreign_keys=[location_id],
        back_populates="requests",
        lazy="selectin",
    )
