import enum

from sqlalchemy import CheckConstraint, Column, Enum, Integer, orm

from src.database.base_class import Base, BaseMixin
from src.exception import InCorrectDataException


class FeeTypeEnum(enum.Enum):
    CASH = "CASH"
    CREDIT = "CREDIT"


# ---------------------------------------------------------------------------
class Fee(Base, BaseMixin):
    __tablename__ = "fee"

    limit = Column(Integer, nullable=False)
    percentage = Column(
        Integer,
        CheckConstraint("percentage >= 0 AND percentage <= 100"),
        nullable=True,
    )
    value = Column(Integer, nullable=True)
    value_limit = Column(Integer, nullable=False)
    type = Column(Enum(FeeTypeEnum), nullable=False)

    @orm.validates("percentage")
    def validate_age(self, key, value):
        if not 0 <= value <= 100:
            raise InCorrectDataException()
        return value
