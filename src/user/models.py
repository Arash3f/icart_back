from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship

from src.agent.models import Agent
from src.cash.models import Cash
from src.credit.models import Credit
from src.database.base_class import Base, BaseMixin
from src.installments.models import Installments
from src.organization.models import Organization
from src.ticket.models import Ticket
from src.user_request.models import UserRequest
from src.wallet.models import Wallet


# ---------------------------------------------------------------------------
class User(Base, BaseMixin):
    __tablename__ = "user"

    username = Column(String, unique=True, index=True)
    national_code = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    first_name = Column(String, index=True, nullable=True)
    last_name = Column(String, index=True, nullable=True)
    subscribe_newsletter = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_valid = Column(Boolean, default=False)
    one_time_password = Column(String, nullable=True)
    expiration_password_at = Column(DateTime(timezone=True), nullable=True)
    phone_number = Column(String, unique=False)

    image_version_id = Column(String, nullable=True)
    image_name = Column(String, nullable=True)

    image_background_version_id = Column(String, nullable=True)
    image_background_name = Column(String, nullable=True)

    # ! Relations
    merchant = relationship("Merchant", uselist=False, back_populates="user")

    installments = relationship(Installments, back_populates="user")

    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id", ondelete="RESTRICT"))
    role = relationship(
        "Role",
        foreign_keys=[role_id],
        back_populates="users",
        lazy="selectin",
    )

    credit_id = Column(UUID(as_uuid=True), ForeignKey("credit.id"))
    credit = relationship(
        Credit,
        foreign_keys=[credit_id],
        back_populates="user",
        lazy="selectin",
    )

    cash_id = Column(UUID(as_uuid=True), ForeignKey("cash.id"))
    cash = relationship(
        Cash,
        foreign_keys=[cash_id],
        back_populates="user",
        lazy="selectin",
    )

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"), nullable=True)
    agent = relationship(Agent, foreign_keys=[agent_id], lazy="selectin")

    self_organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organization.id"),
        nullable=True,
    )
    self_organization = relationship(Organization, foreign_keys=[self_organization_id])

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organization.id"),
        nullable=True,
    )
    organization = relationship(
        "Organization",
        foreign_keys=[organization_id],
        backref="users",
    )

    wallet = relationship(Wallet, uselist=False, back_populates="user", lazy="selectin")

    user_request = relationship(
        UserRequest,
        uselist=False,
        back_populates="user",
        lazy="selectin",
    )

    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"))
    location = relationship(
        "Location",
        foreign_keys=[location_id],
        back_populates="users",
        lazy="selectin",
    )

    ticket_messages = relationship("TicketMessage", back_populates="creator")
    tickets = relationship(Ticket, back_populates="creator")
    user_messages = relationship("UserMessage", back_populates="user")
