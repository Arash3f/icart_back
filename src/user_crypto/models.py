from sqlalchemy import UUID, Column, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.crypto.models import Crypto
from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class UserCrypto(Base, BaseMixin):
    __tablename__ = "user_crypto"

    amount = Column(Float, default=0.0)

    # ! Relations
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"))
    wallet = relationship("Wallet", foreign_keys=[wallet_id], back_populates="cryptos")

    crypto_id = Column(UUID(as_uuid=True), ForeignKey("crypto.id"))
    crypto = relationship(
        Crypto,
        foreign_keys=[crypto_id],
        back_populates="user_cryptos",
    )
