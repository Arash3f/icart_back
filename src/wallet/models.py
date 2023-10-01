from sqlalchemy import UUID, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.capital_transfer.models import CapitalTransfer
from src.database.base_class import Base, BaseMixin
from src.user_crypto.models import UserCrypto


# ---------------------------------------------------------------------------
class Wallet(Base, BaseMixin):
    __tablename__ = "wallet"

    cash_balance = Column(Integer, default=0)
    credit_balance = Column(Integer, default=0)
    number = Column(String, unique=True, index=True)

    # ! Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="wallet",
        lazy="selectin",
    )

    capital_transfer_receiver = relationship(CapitalTransfer, back_populates="receiver")

    cards = relationship("Card", back_populates="wallet")

    cryptos = relationship(UserCrypto, back_populates="wallet")
