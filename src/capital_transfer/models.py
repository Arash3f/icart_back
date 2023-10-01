import enum

from sqlalchemy import UUID, Boolean, Column, Enum, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class CapitalTransferEnum(enum.Enum):
    Cash = "Cash"
    Credit = "Credit"


# todo: Icart Transfer and Swipe Transfer
# ---------------------------------------------------------------------------
class CapitalTransfer(Base, BaseMixin):
    __tablename__ = "capital_transfer"

    value = Column(Float, nullable=False)
    transfer_type = Column(Enum(CapitalTransferEnum))
    finish = Column(Boolean, default=False)

    file_version_id = Column(String, nullable=True)
    file_name = Column(String, nullable=True)

    # ! Relations
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"))
    receiver = relationship("Wallet", back_populates="capital_transfer_receiver")
