from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.important_data.exception import ImportantDataNotFoundException
from src.important_data.models import ImportantData
from src.important_data.schema import ImportantDataUpdate


# ---------------------------------------------------------------------------
class ImportantDataCRUD(BaseCRUD[ImportantData, None, ImportantDataUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        important_data_id: UUID,
    ) -> Type[ImportantData]:
        """
        ! Verify ImportantData Existence

        Parameters
        ----------
        db
            Target database connection
        important_data_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
         ImportantDataNotFoundException
        """
        obj = await db.get(entity=self.model, ident=important_data_id)
        if not obj:
            raise ImportantDataNotFoundException()
        return obj

    async def get_important_data_count(self, *, db: AsyncSession) -> int:
        """
        ! ImportantData Count

        Parameters
        ----------
        db
            Target database connection

        Returns
        -------
        count
            All system important data count

        """
        response = await db.execute(select(self.model))
        count = len(response.scalars().all())

        return count

    async def get_blue_card_cost(self, *, db: AsyncSession) -> int:
        """
        ! Get blue card cost

        Parameters
        ----------
        db
            Target database connection

        Returns
        -------
        count
            All system important data count
        """
        response = await db.execute(select(self.model))
        data = response.scalars().first()

        return data.blue_card_cost

    async def get_register_cost(self, *, db: AsyncSession) -> int:
        """
        ! Get register credit card cost

        Parameters
        ----------
        db
            Target database connection

        Returns
        -------
        count
            All system important data count
        """
        response = await db.execute(select(self.model))
        data = response.scalars().first()

        return data.registration_fee


# ---------------------------------------------------------------------------
important_data = ImportantDataCRUD(ImportantData)
