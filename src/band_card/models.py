from sqlalchemy import (Column,
                        String,
                        ForeignKey,
                        Boolean,
                        UUID,
                        Integer)
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# -----------------------------------------------------
class BankCard(Base, BaseMixin):
    card_number = Column(String, unique=True, index=True)
    shaba_number = Column(String, unique=True, index=True)
    is_verified = Column(Boolean, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="bank_cards"
    )
