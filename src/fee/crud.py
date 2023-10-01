from typing import Type
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.fee.exception import (
    FeeLimitIsDuplicatedException,
    FeeNotFoundException,
)
from src.fee.models import Fee
from src.fee.schema import FeeCreate, FeeUpdate


# ---------------------------------------------------------------------------
class FeeCRUD(BaseCRUD[Fee, FeeCreate, FeeUpdate]):
    async def verify_existence(self, *, db: AsyncSession, fee_id: UUID) -> Type[Fee]:
        """
        ! Verify Fee Existence

        Parameters
        ----------
        db
            Target database connection
        fee_id
            Target fee's ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        FeeNotFoundException
        """
        obj = await db.get(entity=self.model, ident=fee_id)
        if not obj:
            raise FeeNotFoundException()

        return obj

    async def verify_duplicate_limit(
        self,
        *,
        db: AsyncSession,
        limit: int,
        exception_limit: int = None,
    ) -> Fee:
        """
        ! Verify fee limit duplicate

        Parameters
        ----------
        db
            Target database connection
        limit
            Target Item limit
        exception_limit
            Exception fee limit

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        FeeLimitIsDuplicatedException
        """
        response = await db.execute(
            select(self.model).where(
                and_(self.model.limit == limit, self.model.limit != exception_limit),
            ),
        )

        obj = response.scalar_one_or_none()
        if obj:
            raise FeeLimitIsDuplicatedException()

        return obj


# ---------------------------------------------------------------------------
fee = FeeCRUD(Fee)
