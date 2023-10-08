import enum

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin
from src.transaction.models import Transaction


# ---------------------------------------------------------------------------
class CapitalTransferEnum(enum.Enum):
    Cash = "Cash"
    Credit = "Credit"


# ---------------------------------------------------------------------------
class CapitalTransfer(Base, BaseMixin):
    __tablename__ = "capital_transfer"

    value = Column(Float, nullable=False)
    transfer_type = Column(Enum(CapitalTransferEnum))
    finish = Column(Boolean, default=False)
    code = Column(Integer, unique=True, index=True, nullable=True)

    file_version_id = Column(String, nullable=True)
    file_name = Column(String, nullable=True)

    # ! Relations
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"), nullable=True)
    receiver = relationship(
        "Wallet",
        back_populates="capital_transfer_receiver",
        nullable=True,
    )

    transaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transaction.id"),
        nullable=True,
    )
    transaction = relationship(
        Transaction,
        foreign_keys=[transaction_id],
        back_populates="capital_transfer",
    )
