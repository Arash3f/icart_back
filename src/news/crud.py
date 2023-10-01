from typing import Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.news.exception import NewsNotFoundException
from src.news.models import News
from src.news.schema import NewsCreate, NewsUpdate


# ---------------------------------------------------------------------------
class NewsCRUD(BaseCRUD[News, NewsCreate, NewsUpdate]):
    async def verify_existence(self, *, db: AsyncSession, news_id: UUID) -> Type[News]:
        """
        ! Verify News Existence

        Parameters
        ----------
        db
            Target database connection
        news_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        NewsNotFoundException
        """
        obj = await db.get(entity=self.model, ident=news_id)
        if not obj:
            raise NewsNotFoundException()

        return obj


# ---------------------------------------------------------------------------
news = NewsCRUD(News)
