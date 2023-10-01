from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Pos(Base, BaseMixin):
    __tablename__ = "pos"

    token = Column(String, nullable=True, index=True, unique=True)

    # ! Relations
    merchant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("merchant.id", ondelete="RESTRICT"),
    )
    merchant = relationship(
        "Merchant",
        foreign_keys=[merchant_id],
        back_populates="poses",
    )
