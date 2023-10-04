from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Cash(Base, BaseMixin):
    __tablename__ = "cash"

    received = Column(Integer, default=0.0)
    paid = Column(Integer, default=0)
    consumed = Column(Integer, default=0.0)
    remaining = Column(Integer, default=0.0)
    transferred = Column(Integer, default=0.0)
    debt = Column(Integer, default=0.0)
    balance = Column(Integer, default=0.0)

    # ! Relations
    user = relationship("User", uselist=False, back_populates="cash", lazy="selectin")
