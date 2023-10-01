from sqlalchemy import UUID, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Contract(Base, BaseMixin):
    __tablename__ = "contract"

    number = Column(String, index=True, unique=True)
    name = Column(String, nullable=True)
    signatory_name = Column(String, nullable=True)
    signatory_position = Column(String, nullable=True)
    employees_number = Column(Integer, nullable=True)

    file_version_id = Column(String, nullable=True)
    file_name = Column(String, nullable=True)

    # ! Relations
    position_request_id = Column(UUID(as_uuid=True), ForeignKey("position_request.id"))
    position_request = relationship(
        "PositionRequest",
        foreign_keys=[position_request_id],
        back_populates="contract",
        lazy="selectin",
    )
