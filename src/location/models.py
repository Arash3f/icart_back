from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin
from src.position_request.models import PositionRequest


# ---------------------------------------------------------------------------
class Location(Base, BaseMixin):
    __tablename__ = "location"

    name = Column(String, index=True, unique=True, nullable=False)

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

    requests = relationship(PositionRequest, back_populates="location")

    children = relationship("Location", back_populates="parent")

    users = relationship("User", back_populates="location")
