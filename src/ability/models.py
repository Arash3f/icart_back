from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Ability(Base, BaseMixin):
    __tablename__ = "ability"
    name = Column(String, unique=True, index=True)

    # ! Relations
    agents = relationship(
        "Agent",
        secondary="agent_ability",
        back_populates="abilities",
    )
    position_requests = relationship(
        "PositionRequest",
        secondary="position_request_ability",
        back_populates="abilities",
    )
