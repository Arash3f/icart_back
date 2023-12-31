import enum

from sqlalchemy import UUID, Column, Enum, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


class TransactionValueType(enum.Enum):
    CASH = "CASH"
    CREDIT = "CREDIT"


# ---------------------------------------------------------------------------
class Transaction(Base, BaseMixin):
    __tablename__ = "transaction"

    value = Column(Float, nullable=False)
    text = Column(String, nullable=False)
    value_type = Column(Enum(TransactionValueType), nullable=False)

    # ! Relations
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"), nullable=False)
    receiver = relationship("Wallet", foreign_keys=[receiver_id], lazy="selectin")

    transferor_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"), nullable=False)
    transferor = relationship("Wallet", foreign_keys=[transferor_id], lazy="selectin")
