import enum

from sqlalchemy import UUID, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin
from src.terminal.models import Terminal


class InvoiceTypeEnum(enum.Enum):
    CASH = "CASH"
    CREDIT = "CREDIT"


# ---------------------------------------------------------------------------
class Invoice(Base, BaseMixin):
    __tablename__ = "invoice"

    number = Column(String, nullable=False)
    icart_number = Column(Integer, index=True, unique=True, nullable=False)
    value = Column(Integer, nullable=False)
    type = Column(Enum(InvoiceTypeEnum), nullable=False)

    # ! Relations

    parent_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id"), nullable=True)
    parent = relationship("Invoice", foreign_keys=[parent_id], back_populates="child")

    child = relationship(
        "Invoice",
        uselist=False,
        back_populates="parent",
        remote_side="Invoice.id",
    )

    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchant.id"), nullable=False)
    merchant = relationship(
        "Merchant",
        foreign_keys=[merchant_id],
        back_populates="invoices",
        lazy="selectin",
    )

    terminals = relationship(Terminal, back_populates="invoice")
