from sqlalchemy import Column, Float
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Credit(Base, BaseMixin):
    __tablename__ = "credit"

    received = Column(Float, default=0.0)
    consumed = Column(Float, default=0.0)
    remaining = Column(Float, default=0.0)
    transferred = Column(Float, default=0.0)
    debt = Column(Float, default=0.0)

    # ! Relations
    user = relationship("User", uselist=False, back_populates="credit", lazy="selectin")
