import enum

from sqlalchemy import UUID, Column, Enum, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


class TransactionValueType(enum.Enum):
    CASH = "CASH"
    CREDIT = "CREDIT"


class TransactionReasonEnum(enum.Enum):
    WALLET_CHARGING = "WALLET_CHARGING"
    PROFIT = "PROFIT"
    PURCHASE = "PURCHASE"
    FEE = "FEE"
    REGISTER = "REGISTER"
    CONTRACT = "CONTRACT"


class TransactionStatusEnum(enum.Enum):
    FAILED = "FAILED"
    ACCEPTED = "ACCEPTED"


# ---------------------------------------------------------------------------
class Transaction(Base, BaseMixin):
    __tablename__ = "transaction"

    value = Column(Float, nullable=False)
    text = Column(String, nullable=False)
    value_type = Column(Enum(TransactionValueType), nullable=False)
    code = Column(String, nullable=True)
    reason = Column(Enum(TransactionReasonEnum), nullable=True)
    status = Column(
        Enum(TransactionStatusEnum),
        nullable=False,
        default=TransactionStatusEnum.ACCEPTED,
    )
    # ! Relations
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"), nullable=False)
    receiver = relationship("Wallet", foreign_keys=[receiver_id], lazy="selectin")

    transferor_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"), nullable=False)
    transferor = relationship("Wallet", foreign_keys=[transferor_id], lazy="selectin")

    intermediary_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"), nullable=True)
    intermediary = relationship(
        "Wallet",
        foreign_keys=[intermediary_id],
        lazy="selectin",
    )

    installments = relationship(
        "Installments",
        uselist=False,
        back_populates="transaction",
    )

    capital_transfer = relationship(
        "CapitalTransfer",
        uselist=False,
        back_populates="transaction",
    )

    transactions_rows = relationship("TransactionRow", back_populates="transaction")


# ---------------------------------------------------------------------------
class TransactionRow(Base, BaseMixin):
    __tablename__ = "transaction_row"

    value = Column(Float, nullable=False)
    text = Column(String, nullable=False)
    value_type = Column(Enum(TransactionValueType), nullable=False)
    code = Column(String, nullable=True)
    reason = Column(Enum(TransactionReasonEnum), nullable=True)
    status = Column(
        Enum(TransactionStatusEnum),
        nullable=False,
        default=TransactionStatusEnum.ACCEPTED,
    )
    # ! Relations
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"), nullable=False)
    receiver = relationship("Wallet", foreign_keys=[receiver_id], lazy="selectin")

    transferor_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"), nullable=False)
    transferor = relationship("Wallet", foreign_keys=[transferor_id], lazy="selectin")

    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transaction.id"))
    transaction = relationship(
        "Transaction",
        foreign_keys=[transaction_id],
        back_populates="transactions_rows",
    )
