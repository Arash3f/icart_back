import enum

from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


class CardEnum(enum.Enum):
    CREDIT = "CREDIT"
    SILVER = "CREDIT"
    GOLD = "GOLD"
    BLUE = "BLUE"
    PLATINUM = "PLATINUM"


# ---------------------------------------------------------------------------
class Card(Base, BaseMixin):
    __tablename__ = "card"

    number = Column(String, unique=True, index=True)
    cvv2 = Column(Integer, nullable=False)
    expiration_at = Column(DateTime(timezone=True), nullable=False)
    password = Column(String, nullable=False)
    dynamic_password = Column(String, nullable=True)
    dynamic_password_exp = Column(DateTime(timezone=True), nullable=True)
    type = Column(Enum(CardEnum), nullable=False)

    # ! Relations
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"))
    wallet = relationship(
        "Wallet",
        foreign_keys=[wallet_id],
        back_populates="cards",
        lazy="selectin",
    )
