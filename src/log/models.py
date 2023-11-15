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
    # ! LOCATION
    ADD_LOCATION = "ADD_LOCATION"
    UPDATE_LOCATION = "UPDATE_LOCATION"
    # ! CAPITAL_TRANSFER
    ADD_CAPITAL_TRANSFER = "ADD_CAPITAL_TRANSFER"
    APPROVE_CAPITAL_TRANSFER = "APPROVE_CAPITAL_TRANSFER"
    # ! FEE
    ADD_FEE = "ADD_FEE"
    DELETE_FEE = "DELETE_FEE"
    UPDATE_FEE = "UPDATE_FEE"
    # ! USER_MESSAGE
    ADD_USER_MESSAGE = "ADD_USER_MESSAGE"
    DELETE_USER_MESSAGE = "DELETE_USER_MESSAGE"
    # ! TICKET
    ADD_TICKET = "ADD_TICKET"
    UPDATE_TICKET = "UPDATE_TICKET"
    # ! NEWS
    ADD_NEWS = "ADD_NEWS"
    DELETE_NEWS = "DELETE_NEWS"
    UPDATE_NEWS = "UPDATE_NEWS"
    # ! ROLE
    ASSIGN_PERMISSION_TO_ROLE = "ASSIGN_PERMISSION_TO_ROLE"
    # ! MERCHANT
    UPDATE_MERCHANT = "UPDATE_MERCHANT"
    # ! POS
    ADD_POS = "ADD_POS"
    DELETE_POS = "DELETE_POS"
    UPDATE_POS = "UPDATE_POS"
    # ! USER
    UPDATE_USER = "UPDATE_USER"
    UPDATE_USER_ACTIVITY = "UPDATE_USER_ACTIVITY"
    # ! ORGANIZATION
    GENERATE_ORGANIZATION_USER = "GENERATE_ORGANIZATION_USER"
    APPEND_ORGANIZATION_USER = "APPEND_ORGANIZATION_USER"
    ACTIVE_ORGANIZATION_USER = "ACTIVE_ORGANIZATION_USER"
    # ! POSITION REQUEST
    UPDATE_POSITION_REQUEST = "UPDATE_POSITION_REQUEST"
    CREATE_POSITION_REQUEST = "CREATE_POSITION_REQUEST"
    APPROVE_POSITION_REQUEST = "APPROVE_POSITION_REQUEST"
    # ! CARD
    BUY_CARD = "BUY_CARD"


# ---------------------------------------------------------------------------
class Log(Base, BaseMixin):
    __tablename__ = "log"

    detail = Column(String, nullable=True)
    type = Column(Enum(LogType), nullable=True)

    # ! Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    user = relationship(
        "User",
        back_populates="logs",
        foreign_keys=[user_id],
        lazy="selectin",
    )
