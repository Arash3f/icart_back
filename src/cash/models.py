from sqlalchemy import Column, BigInteger
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Cash(Base, BaseMixin):
    __tablename__ = "cash"

    balance = Column(BigInteger, default=0)
    cash_back = Column(BigInteger, default=0)

    # ! Maybe it will be used in the future
    received = Column(BigInteger, default=0)
    consumed = Column(BigInteger, default=0)
    transferred = Column(BigInteger, default=0)
    debt = Column(BigInteger, default=0)

    # ! Relations
    user = relationship("User", uselist=False, back_populates="cash", lazy="selectin")
