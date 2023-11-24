from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    UUID,
)
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# -----------------------------------------------------
class BankCard(Base, BaseMixin):
    __tablename__ = "bank_card"

    card_number = Column(String, unique=True, index=True)
    shaba_number = Column(String, unique=True, index=True)

    # ! Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="bank_cards",
    )

    withdraws = relationship("BankCard", back_populates="bank_card")
