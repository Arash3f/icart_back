from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.credit.exception import CreditNotFoundException
from src.credit.models import Credit
from src.database.base_crud import BaseCRUD


# ---------------------------------------------------------------------------
class CreditCRUD(BaseCRUD[Credit, None, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        credit_id: UUID,
    ) -> Type[Credit]:
        """
        ! Verify Credit Existence

        Parameters
        ----------
        db
            Target database connection
        credit_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        CreditNotFoundException
        """
        obj = await db.get(entity=self.model, ident=credit_id)
        if not obj:
            raise CreditNotFoundException()

        return obj

    async def find_by_user_id(self, *, db: AsyncSession, user_id: UUID) -> Credit:
        """
        ! Find Credit by user id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target Credit User ID

        Returns
        -------
        credit
            Found Item

        Raises
        ------
        CreditNotFoundException
        """
        response = await db.execute(
            select(self.model).where(self.model.user.id == user_id),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise CreditNotFoundException()

        return obj


# ---------------------------------------------------------------------------
credit = CreditCRUD(Credit)
