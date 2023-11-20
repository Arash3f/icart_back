from sqlalchemy import Column, BigInteger, Boolean
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Credit(Base, BaseMixin):
    __tablename__ = "credit"

    balance = Column(BigInteger, default=0)
    paid = Column(BigInteger, default=0)
    considered = Column(BigInteger, default=0)
    remaining = Column(BigInteger, default=0)
    received = Column(BigInteger, default=0)
    debt = Column(BigInteger, default=0)
    active = Column(Boolean, default=False)
    credit_back = Column(BigInteger, default=0)
    used = Column(BigInteger, default=0)

    # ! Maybe it will be used in the future
    consumed = Column(BigInteger, default=0)
    transferred = Column(BigInteger, default=0)

    # ! Relations
    user = relationship("User", uselist=False, back_populates="credit", lazy="selectin")
