from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Crypto(Base, BaseMixin):
    __tablename__ = "crypto"

    name = Column(String, unique=True, index=True)

    # ! Relations
    user_cryptos = relationship("UserCrypto", back_populates="crypto")
