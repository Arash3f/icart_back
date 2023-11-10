from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Log(Base, BaseMixin):
    __tablename__ = "log"

    detail = Column(String, nullable=True)

    # ! Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship(
        "User",
        back_populates="logs",
        foreign_keys=[user_id],
        lazy="selectin",
    )
