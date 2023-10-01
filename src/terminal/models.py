from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Terminal(Base, BaseMixin):
    __tablename__ = "terminal"

    number = Column(String, index=True, unique=True, nullable=False)
    redirect_url = Column(String, nullable=False)

    # ! Relations
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id"), nullable=True)
    invoice = relationship(
        "Invoice",
        foreign_keys=[invoice_id],
        back_populates="terminals",
        lazy="selectin",
    )
