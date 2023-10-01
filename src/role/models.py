from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin
from src.permission.models import Permission


# ---------------------------------------------------------------------------
class Role(Base, BaseMixin):
    __tablename__ = "role"
    name = Column(String, index=True, nullable=False)

    # !Relations
    permissions = relationship(
        Permission,
        lazy="selectin",
        secondary="role_permission",
        back_populates="roles",
    )
    users = relationship("User", back_populates="role", lazy="selectin")


# ---------------------------------------------------------------------------
class RolePermission(Base, BaseMixin):
    __tablename__ = "role_permission"
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"))
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permission.id"))
