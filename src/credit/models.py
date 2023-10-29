from sqlalchemy import Column, Integer, String, BigInteger, Boolean
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Credit(Base, BaseMixin):
    __tablename__ = "credit"

    considered = Column(BigInteger, default=0)
    received = Column(BigInteger, default=0.0)
    paid = Column(BigInteger, default=0)
    consumed = Column(BigInteger, default=0.0)
    remaining = Column(BigInteger, default=0.0)
    transferred = Column(BigInteger, default=0.0)
    debt = Column(BigInteger, default=0.0)
    balance = Column(BigInteger, default=0.0)
    active = Column(Boolean, default=False)

    # ! Relations
    user = relationship("User", uselist=False, back_populates="credit", lazy="selectin")
