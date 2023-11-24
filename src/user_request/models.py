from sqlalchemy import UUID, Column, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class UserRequest(Base, BaseMixin):
    __tablename__ = "user_request"

    birth_place = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    father_name = Column(String, nullable=True)
    tel = Column(String, nullable=True)
    address = Column(String, nullable=True)
    reason = Column(String, nullable=True)

    status = Column(Boolean, default=True)

    national_card_front_version_id = Column(String, nullable=True)
    national_card_front_name = Column(String, nullable=True)

    national_card_back_version_id = Column(String, nullable=True)
    national_card_back_name = Column(String, nullable=True)

    birth_certificate_version_id = Column(String, nullable=True)
    birth_certificate_name = Column(String, nullable=True)

    video_version_id = Column(String, nullable=True)
    video_name = Column(String, nullable=True)

    # ! Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="user_request",
        lazy="selectin",
    )

    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id"))
    location = relationship(
        "Location",
        foreign_keys=[location_id],
        back_populates="user_requests",
        lazy="selectin",
    )
