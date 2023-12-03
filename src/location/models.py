from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.cooperation_request.models import CooperationRequest
from src.database.base_class import Base, BaseMixin
from src.position_request.models import PositionRequest


# ---------------------------------------------------------------------------
class Location(Base, BaseMixin):
    __tablename__ = "location"

    name = Column(String, index=True, nullable=False)

    # ! Relations
    parent_id = Column(UUID(as_uuid=True), ForeignKey("location.id"), nullable=True)
    parent = relationship(
        "Location",
        back_populates="children",
        remote_side="Location.id",
        lazy="selectin",
    )

    agents = relationship(
        "Agent",
        secondary="agent_location",
        back_populates="locations",
    )

    organizations = relationship("Organization", back_populates="location")

    merchants = relationship("Merchant", back_populates="location")

    requests = relationship(PositionRequest, back_populates="location")

    cooperation_requests = relationship(CooperationRequest, back_populates="location")

    children = relationship("Location", back_populates="parent", lazy="selectin")

    users = relationship("User", back_populates="location")

    user_requests = relationship("UserRequest", back_populates="location")
