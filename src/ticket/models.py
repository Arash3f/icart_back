import enum

from sqlalchemy import UUID, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin
from src.ticket_message.models import TicketMessage


# ---------------------------------------------------------------------------
class TicketType(enum.Enum):
    TECHNICAL = "TECHNICAL"
    SALES = "SALES"


# ---------------------------------------------------------------------------
class TicketPosition(enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSE = "CLOSE"


# ---------------------------------------------------------------------------
class Ticket(Base, BaseMixin):
    __tablename__ = "ticket"

    title = Column(String, nullable=False)
    importance = Column(Integer, default=0)
    type = Column(Enum(TicketType), nullable=False)
    position = Column(Enum(TicketPosition), default=TicketPosition.OPEN)
    number = Column(Integer, index=True, unique=True, nullable=False)

    # ! Relations
    messages = relationship(
        TicketMessage,
        back_populates="ticket",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="desc(TicketMessage.created_at)",
    )

    creator_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    creator = relationship("User", foreign_keys=[creator_id], back_populates="tickets")
