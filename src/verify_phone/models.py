from sqlalchemy import Column, DateTime, Integer, String

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class VerifyPhone(Base, BaseMixin):
    __tablename__ = "verify_phone"

    phone_number = Column(String, unique=True, index=True, nullable=False)
    verify_code = Column(Integer, unique=True, index=True, nullable=False)
    expiration_code_at = Column(DateTime(timezone=True), nullable=False)
