from sqlalchemy import UUID, Boolean, Column, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.ability.models import Ability
from src.database.base_class import Base, BaseMixin
from src.location.models import Location
from src.merchant.models import Merchant
from src.organization.models import Organization


# ---------------------------------------------------------------------------
class Agent(Base, BaseMixin):
    __tablename__ = "agent"

    is_main = Column(Boolean, default=False)
    profit_rate = Column(Float, default=0)

    # # ! Relations
    parent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"), nullable=True)
    parent = relationship(
        "Agent",
        back_populates="children",
        remote_side="Agent.id",
        lazy="selectin",
    )

    agent_user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", use_alter=True))
    agent_user = relationship("User", foreign_keys=[agent_user_id], lazy="selectin")

    organization = relationship(Organization, back_populates="agent", lazy="selectin")

    merchants = relationship(Merchant, back_populates="agent", lazy="selectin")

    abilities = relationship(
        Ability,
        secondary="agent_ability",
        back_populates="agents",
        lazy="selectin",
    )

    children = relationship("Agent", back_populates="parent")

    locations = relationship(
        Location,
        secondary="agent_location",
        back_populates="agents",
        lazy="selectin",
    )


# ---------------------------------------------------------------------------
class AgentAbility(Base, BaseMixin):
    __tablename__ = "agent_ability"
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"))
    ability_id = Column(UUID(as_uuid=True), ForeignKey("ability.id"))


# ---------------------------------------------------------------------------
class AgentLocation(Base, BaseMixin):
    __tablename__ = "agent_location"
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"))
    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"))
