from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cash.exception import CashNotFoundException
from src.cash.models import Cash
from src.database.base_crud import BaseCRUD
from src.user.models import User


# ---------------------------------------------------------------------------
class CashCRUD(BaseCRUD[Cash, None, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        cash_id: UUID,
    ) -> Type[Cash]:
        """
        ! Verify Cash Existence

        Parameters
        ----------
        db
            Target database connection
        cash_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        CashNotFoundException
        """
        obj = await db.get(entity=self.model, ident=cash_id)
        if not obj:
            raise CashNotFoundException()

        return obj

    async def find_by_user_id(self, *, db: AsyncSession, user: User) -> Cash:
        """
        ! Verify cash existence by user_id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target user id

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        PosNotFoundException
        """
        response = await db.execute(
            select(self.model).where(self.model.user == user),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise CashNotFoundException()

        return obj


# ---------------------------------------------------------------------------
cash = CashCRUD(Cash)
