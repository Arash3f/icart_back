from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class Permission(Base, BaseMixin):
    __tablename__ = "permission"
    name = Column(String, index=True, nullable=False)
    code = Column(Integer, unique=True, nullable=False)

    # ! Relations
    roles = relationship(
        "Role",
        secondary="role_permission",
        back_populates="permissions",
    )
