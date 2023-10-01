from sqlalchemy import UUID, Column, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class TicketMessage(Base, BaseMixin):
    __tablename__ = "ticket_message"

    text = Column(Text, nullable=False)

    # ! Relations
    creator_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    creator = relationship(
        "User",
        foreign_keys=[creator_id],
        back_populates="ticket_messages",
    )

    ticket_id = Column(UUID(as_uuid=True), ForeignKey("ticket.id"))
    ticket = relationship("Ticket", foreign_keys=[ticket_id])
