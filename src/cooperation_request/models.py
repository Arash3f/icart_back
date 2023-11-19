import enum

from sqlalchemy import Column, Enum, Integer, String, ForeignKey, UUID, Boolean
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


class CooperationType(enum.Enum):
    AGENT = "AGENT"
    ORGANIZATION = "ORGANIZATION"
    MERCHANT = "MERCHANT"
    SALES_AGENT = "SALES_AGENT"


class CooperationRequestFieldOfWorkType(enum.Enum):
    HAIR_TRANSPLANT = "HAIR_TRANSPLANT"
    BEAUTY_CLINICS = "BEAUTY_CLINICS"
    DENTAL_CLINICS = "DENTAL_CLINICS"
    FACIAL_GEL_BOTOX = "FACIAL_GEL_BOTOX"
    FURNITURE_STORES = "FURNITURE_STORES"
    ELECTRICAL_APPLIANCES_STORE = "ELECTRICAL_APPLIANCES_STORE"
    SLEEP_GOODS_STORES = "SLEEP_GOODS_STORES"
    CARPET = "CARPET"
    ELECTRICAL_APPLIANCES_REPAIRS = "ELECTRICAL_APPLIANCES_REPAIRS"
    LAPTOP = "LAPTOP"
    MOBILE = "MOBILE"
    DIGITAL_ACCESSORIES = "DIGITAL_ACCESSORIES"
    TRAVEL_AGENCY = "TRAVEL_AGENCY"
    RECREATIONAL_SPORTS_CENTERS = "RECREATIONAL_SPORTS_CENTERS"
    LANGUAGE_TEACHING = "LANGUAGE_TEACHING"
    HAIRDRESSING_TRAINING = "HAIRDRESSING_TRAINING"
    STATIONERY = "STATIONERY"
    WATCH_GALLERY = "WATCH_GALLERY"
    GOLD_SALES = "GOLD_SALES"
    JEWELRY_ACCESSORIES = "JEWELRY_ACCESSORIES"
    SUPER_MARKET = "SUPER_MARKET"
    FRUIT_SHOP = "FRUIT_SHOP"
    DAIRY = "DAIRY"
    CAFE_RESTAURANT_FAST_FOOD = "CAFE_RESTAURANT_FAST_FOOD"
    CONFECTIONERY_DRIED_FRUIT = "CONFECTIONERY_DRIED_FRUIT"
    ASIA_INSURANCE = "ASIA_INSURANCE"
    THIRD_PARTY_INSURANCE = "THIRD_PARTY_INSURANCE"
    ADULT_CLOTHING = "ADULT_CLOTHING"
    CHILDREN_CLOTHING = "CHILDREN_CLOTHING"
    BAGS_AND_SHOES = "BAGS_AND_SHOES"
    INTERIOR_DECORATION_DESIGNER = "INTERIOR_DECORATION_DESIGNER"
    BUILDING_EQUIPMENT = "BUILDING_EQUIPMENT"
    MESON = "MESON"
    CAR_REPAIRS = "CAR_REPAIRS"
    PHARMACY = "PHARMACY"
    KITCHEN_ACCESSORIES_STORE = "KITCHEN_ACCESSORIES_STORE"
    EDUCATIONAL_SERVICES = "EDUCATIONAL_SERVICES"
    HOME_APPLIANCES = "HOME_APPLIANCES"
    AUDIO_AND_VIDEO_PRODUCT_STORE = "AUDIO_AND_VIDEO_PRODUCT_STORE"
    BAKERY = "BAKERY"
    GROCERY_STORES = "GROCERY_STORES"
    STATIONERY_STORES = "STATIONERY_STORES"
    DTY_FRUITS_SHOP = "DTY_FRUITS_SHOP"
    CLINICS = "CLINICS"
    CLOTHING_STORES = "CLOTHING_STORES"
    HAIRDRESSERS = "HAIRDRESSERS"
    LASER_CENTERS = "LASER_CENTERS"
    GOLD_AND_SILVER = "GOLD_AND_SILVER"
    WATCH_SHOP = "WATCH_SHOP"
    PERFUME_AND_COLOGNE_STORE = "PERFUME_AND_COLOGNE_STORE"
    DECORATION = "DECORATION"
    COSMETIC = "COSMETIC"
    PROTEIN_STORE = "PROTEIN_STORE"
    CHANDELIERS_AND_ELECTRICAL_APPLIANCES = "CHANDELIERS_AND_ELECTRICAL_APPLIANCES"


# ---------------------------------------------------------------------------
class CooperationRequest(Base, BaseMixin):
    __tablename__ = "cooperation_request"

    name = Column(String, nullable=False)
    tel = Column(String, nullable=False)
    requester_name = Column(String, nullable=False)
    type = Column(Enum(CooperationType), default=CooperationType.AGENT)
    status = Column(Boolean, default=False)

    field_of_work = Column(Enum(CooperationRequestFieldOfWorkType), nullable=True)
    employee_count = Column(Integer, nullable=True)

    # ! relations
    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"))
    location = relationship(
        "Location",
        foreign_keys=[location_id],
        back_populates="cooperation_requests",
        lazy="selectin",
    )