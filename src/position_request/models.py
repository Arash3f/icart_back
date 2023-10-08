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
class PositionRequest(Base, BaseMixin):
    __tablename__ = "position_request"

    name = Column(String, nullable=True)
    field_of_work = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    tel = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    employee_count = Column(Integer, nullable=True)
    is_approve = Column(Boolean, default=False)
    target_position = Column(Enum(PositionRequestType))
    status = Column(
        Enum(PositionRequestStatusType),
        default=PositionRequestStatusType.OPEN,
    )
    number = Column(Integer, unique=True, index=True, nullable=True)

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
