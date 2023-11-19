import enum

from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


class CardEnum(enum.Enum):
    CREDIT = "CREDIT"
    SILVER = "SILVER"
    GOLD = "GOLD"
    BLUE = "BLUE"
    PLATINUM = "PLATINUM"


# ---------------------------------------------------------------------------
class Card(Base, BaseMixin):
    __tablename__ = "card"

    number = Column(String, unique=True, index=True)
    cvv2 = Column(Integer, nullable=False)
    expiration_at = Column(DateTime(timezone=True), nullable=True)
    password = Column(String, nullable=False)
    dynamic_password = Column(String, nullable=True)
    dynamic_password_exp = Column(DateTime(timezone=True), nullable=True)
    forget_password = Column(String, nullable=True)
    forget_password_exp = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    type = Column(Enum(CardEnum), nullable=False)

    # ! Relations
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"))
    wallet = relationship(
        "Wallet",
        foreign_keys=[wallet_id],
        back_populates="cards",
        lazy="selectin",
    )
