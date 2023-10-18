from sqlalchemy import UUID, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Installments(Base, BaseMixin):
    __tablename__ = "installments"

    number = Column(String, index=True, nullable=False, unique=True)
    value = Column(Integer, nullable=False)
    due_date = Column(DateTime(timezone=True))

    # ! Relations
    parent_id = Column(UUID(as_uuid=True), ForeignKey("installments.id"), nullable=True)
    parent = relationship(
        "Installments",
        foreign_keys=[parent_id],
        back_populates="child",
    )

    child = relationship(
        "Installments",
        uselist=False,
        back_populates="parent",
        remote_side="Installments.id",
    )

    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchant.id"), nullable=False)
    merchant = relationship(
        "Merchant",
        foreign_keys=[merchant_id],
        back_populates="installments",
        lazy="selectin",
    )

    transaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transaction.id"),
        nullable=True,
    )
    transaction = relationship(
        "Transaction",
        foreign_keys=[transaction_id],
        back_populates="installments",
    )

    invoice = relationship("Invoice", uselist=False, back_populates="installments")
