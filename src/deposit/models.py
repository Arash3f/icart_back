from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    UUID,
    ForeignKey,
    String,
)

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Deposit(Base, BaseMixin):
    __tablename__ = "deposit"

    amount = Column(Integer, nullable=False)
    zibal_track_id = Column(String, nullable=False)

    # ! Relations
    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wallet.id"),
        index=True,
    )
    wallet = relationship(
        "Wallet",
        foreign_keys=[wallet_id],
        back_populates="deposits",
        lazy="selectin",
    )
