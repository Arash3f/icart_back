import enum

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    BigInteger,
)
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin
from src.transaction.models import Transaction


# ---------------------------------------------------------------------------
class CapitalTransferEnum(enum.Enum):
    Cash = "Cash"
    Credit = "Credit"


# ---------------------------------------------------------------------------
class CapitalTransferStatusEnum(enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    ACCEPTED = "ACCEPTED"


# ---------------------------------------------------------------------------
class CapitalTransfer(Base, BaseMixin):
    __tablename__ = "capital_transfer"

    value = Column(BigInteger, nullable=False)
    transfer_type = Column(Enum(CapitalTransferEnum))
    finish = Column(Boolean, default=False)
    code = Column(Integer, unique=True, index=True, nullable=True)
    status = Column(
        Enum(CapitalTransferStatusEnum),
        nullable=False,
        default=CapitalTransferStatusEnum.IN_PROGRESS,
    )

    file_version_id = Column(String, nullable=True)
    file_name = Column(String, nullable=True)

    # ! Relations
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"))
    receiver = relationship(
        "Wallet",
        back_populates="capital_transfer_receiver",
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
