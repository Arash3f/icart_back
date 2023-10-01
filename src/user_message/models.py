from sqlalchemy import UUID, Boolean, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class UserMessage(Base, BaseMixin):
    __tablename__ = "user_message"

    title = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    status = Column(Boolean, default=False)

    # ! Relation
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship("User", foreign_keys=[user_id], back_populates="user_messages")
