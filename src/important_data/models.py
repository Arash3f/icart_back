from sqlalchemy import Column, Integer

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class ImportantData(Base, BaseMixin):
    __tablename__ = "important_data"

    registration_fee = Column(Integer, nullable=False)
    blue_card_cost = Column(Integer, nullable=True)
