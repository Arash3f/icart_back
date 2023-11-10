import enum

from sqlalchemy import UUID, Column, ForeignKey, String, Enum
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


class LogType(enum.Enum):
    # ! ROLE
    DELETE_ROLE = "DELETE_ROLE"
    ADD_ROLE = "ADD_ROLE"
    UPDATE_ROLE = "UPDATE_ROLE"
    # ! AGENT
    UPDATE_AGENT = "UPDATE_AGENT"
    # ! ABILITY
    DELETE_ABILITY = "DELETE_ABILITY"
    ADD_ABILITY = "ADD_ABILITY"
    UPDATE_ABILITY = "UPDATE_ABILITY"


# ---------------------------------------------------------------------------
class Log(Base, BaseMixin):
    __tablename__ = "log"

    detail = Column(String, nullable=True)
    type = Column(Enum(LogType), nullable=True)

    # ! Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship(
        "User",
        back_populates="logs",
        foreign_keys=[user_id],
        lazy="selectin",
    )
