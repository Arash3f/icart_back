from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.contract.models import Contract
from src.database.base_class import Base, BaseMixin
from src.invoice.models import Invoice
from src.pos.models import Pos


# ---------------------------------------------------------------------------
class Merchant(Base, BaseMixin):
    __tablename__ = "merchant"

    number = Column(String, index=True, unique=True, nullable=False)

    # ! Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship("User", foreign_keys=[user_id], back_populates="merchant")

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"))
    agent = relationship("Agent", foreign_keys=[agent_id])

    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"), nullable=True)
    location = relationship(
        "Location",
        foreign_keys=[location_id],
        back_populates="merchants",
    )

    contract = relationship(
        Contract,
        uselist=False,
        back_populates="merchant",
        lazy="selectin",
    )

    invoices = relationship(Invoice, back_populates="merchant")

    poses = relationship(Pos, back_populates="merchant")
