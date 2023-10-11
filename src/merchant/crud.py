from typing import Type
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.merchant.exception import MerchantNotFoundException
from src.merchant.models import Merchant
from src.user.models import User


# ---------------------------------------------------------------------------
class MerchantCRUD(BaseCRUD[Merchant, None, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        merchant_id: UUID,
    ) -> Type[Merchant]:
        """
        ! Verify Merchant Existence

        Parameters
        ----------
        db
            Target database connection
        merchant_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        MerchantNotFoundException
        """
        obj = await db.get(entity=self.model, ident=merchant_id)
        if not obj:
            raise MerchantNotFoundException()

        return obj

    async def find_by_user_id(self, *, db: AsyncSession, user_id: UUID) -> Merchant:
        """
        ! Find Merchant By user id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target Agent user ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        MerchantNotFoundException
        """
        response = await db.execute(
            select(self.model).where(Merchant.user_id == user_id),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise MerchantNotFoundException()

        return obj

    async def verify_existence_by_number(
        self,
        *,
        db: AsyncSession,
        merchant_number: str,
    ) -> Merchant:
        """
        ! Verify Merchant Existence By number

        Parameters
        ----------
        db
            Target database connection
        merchant_number
            Target Merchant number

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        MerchantNotFoundException
        """
        response = await db.execute(
            select(self.model).where(Merchant.number == merchant_number),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise MerchantNotFoundException()

        return obj

    async def get_merchant_users_count_by_agent_id(
        self,
        *,
        db: AsyncSession,
        agent_id: UUID,
    ) -> bool:
        response = await db.execute(
            select(func.count())
            .select_from(Merchant)
            .where(
                Merchant.agent_id == agent_id,
            ),
        )
        merchent_users_count = response.scalar()

        return merchent_users_count


# ---------------------------------------------------------------------------
merchant = MerchantCRUD(Merchant)
