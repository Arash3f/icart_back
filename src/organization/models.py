from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Organization(Base, BaseMixin):
    __tablename__ = "organization"

    name = Column(String, index=True)

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

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"))
    agent = relationship("Agent", foreign_keys=[agent_id])
