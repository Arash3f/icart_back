from sqlalchemy import UUID, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin
from src.invoice.models import Invoice
from src.pos.models import Pos


# ---------------------------------------------------------------------------
class Merchant(Base, BaseMixin):
    __tablename__ = "merchant"

    earned_credit = Column(Integer, default=0)
    number = Column(String, index=True, unique=True, nullable=False)

    # ! Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship("User", foreign_keys=[user_id], back_populates="merchant")

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"))
    agent = relationship("Agent", foreign_keys=[agent_id])

    invoices = relationship(Invoice, back_populates="merchant")

    poses = relationship(Pos, back_populates="merchant")
