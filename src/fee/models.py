import enum

from sqlalchemy import CheckConstraint, Column, Enum, Integer, Float, BigInteger

from src.database.base_class import Base, BaseMixin


class FeeTypeEnum(enum.Enum):
    CASH = "CASH"
    CREDIT = "CREDIT"


class FeeUserType(enum.Enum):
    USER = "USER"
    MERCHANT = "MERCHANT"


# ---------------------------------------------------------------------------
class Fee(Base, BaseMixin):
    __tablename__ = "fee"

    limit = Column(BigInteger, nullable=False)

    type = Column(Enum(FeeTypeEnum), nullable=False, default=FeeTypeEnum.CASH)
    user_type = Column(Enum(FeeUserType), nullable=False, default=FeeUserType.USER)

    percentage = Column(
        Float,
        CheckConstraint("percentage >= 0 AND percentage <= 100"),
        nullable=True,
    )
    value = Column(Integer, nullable=True)
