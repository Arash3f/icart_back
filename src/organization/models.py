from sqlalchemy import UUID, Column, ForeignKey
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Organization(Base, BaseMixin):
    __tablename__ = "organization"

    # ! Relations
    user_organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id", use_alter=True),
    )
    user_organization = relationship(
        "User",
        foreign_keys=[user_organization_id],
        lazy="selectin",
    )

    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"), nullable=True)
    location = relationship(
        "Location",
        foreign_keys=[location_id],
        back_populates="organizations",
    )

    # users = relationship("User", back_populates="organization")

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"))
    agent = relationship("Agent", foreign_keys=[agent_id])
