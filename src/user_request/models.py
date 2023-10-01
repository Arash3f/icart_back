from sqlalchemy import UUID, Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.agent.models import Agent
from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class UserRequest(Base, BaseMixin):
    __tablename__ = "user_request"

    first_name = Column(String, index=True, nullable=True)
    last_name = Column(String, index=True, nullable=True)
    image_version_id = Column(String, nullable=True)
    subscribe_newsletter = Column(Boolean, default=False)
    father_name = Column(String, nullable=True)
    birth_place = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    tel = Column(String, nullable=True)
    address = Column(String, nullable=True)

    # ! Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"), nullable=True)
    user = relationship(Agent, foreign_keys=[user_id], lazy="selectin")

    province_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"), nullable=True)
    province = relationship(Agent, foreign_keys=[province_id], lazy="selectin")

    city_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"), nullable=True)
    city = relationship(Agent, foreign_keys=[city_id], lazy="selectin")
