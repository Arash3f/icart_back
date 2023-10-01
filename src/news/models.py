from sqlalchemy import Column, String, Text

from src.database.base_class import Base, BaseMixin


# ---------------------------------------------------------------------------
class News(Base, BaseMixin):
    __tablename__ = "news"

    title = Column(String, index=True, nullable=False)
    text = Column(Text, nullable=False)
