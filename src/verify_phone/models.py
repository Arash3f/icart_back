import enum

from sqlalchemy import Column, DateTime, Integer, String, Enum

from src.database.base_class import Base, BaseMixin


class VerifyPhoneType(enum.Enum):
    FORGET_PASSWORD = "FORGET_PASSWORD"
    REGISTER = "REGISTER"


# ---------------------------------------------------------------------------
class VerifyPhone(Base, BaseMixin):
    __tablename__ = "verify_phone"

    phone_number = Column(String, unique=True, index=True, nullable=False)
    verify_code = Column(Integer, index=True, nullable=False)
    expiration_code_at = Column(DateTime(timezone=True), nullable=False)

    type = Column(Enum(VerifyPhoneType), default=VerifyPhoneType.REGISTER)
