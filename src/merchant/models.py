from sqlalchemy import UUID, Column, ForeignKey, String, Enum
from sqlalchemy.orm import relationship

from src.contract.models import Contract
from src.database.base_class import Base, BaseMixin
from src.installments.models import Installments
from src.pos.models import Pos
from src.position_request.models import FieldOfWorkType, SellingType


# ---------------------------------------------------------------------------
class Merchant(Base, BaseMixin):
    __tablename__ = "merchant"

    number = Column(String, index=True, unique=True, nullable=False)
    field_of_work = Column(Enum(FieldOfWorkType), nullable=True)
    selling_type = Column(Enum(SellingType), default=SellingType.ALL_THREE)
    geo = Column(String, nullable=True)

    # ! Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="merchant",
        lazy="selectin",
    )

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"))
    agent = relationship("Agent", foreign_keys=[agent_id], lazy="selectin")

    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"), nullable=True)
    location = relationship(
        "Location",
        foreign_keys=[location_id],
        back_populates="merchants",
        lazy="selectin",
    )

    contract = relationship(
        Contract,
        uselist=False,
        back_populates="merchant",
        lazy="selectin",
    )

    installments = relationship(Installments, back_populates="merchant")

    poses = relationship(Pos, back_populates="merchant")
