import uuid

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


# ---------------------------------------------------------------------------
class BaseMixin:
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        unique=True,
        default=uuid.uuid4,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ---------------------------------------------------------------------------
Base = declarative_base()
