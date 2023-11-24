from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    UUID,
    ForeignKey,
    Boolean,
)

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Withdraw(Base, BaseMixin):
    __tablename__ = "withdraw"

    amount = Column(Integer, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_done = Column(Boolean, default=False)

    # ! Relations
    bank_card_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bank_card.id"),
        index=True,
    )
    bank_card = relationship(
        "BankCard",
        foreign_keys=[bank_card_id],
        back_populates="withdraws",
        lazy="selectin",
    )
