from random import randint
from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.wallet.exception import WalletNotFoundException
from src.wallet.models import Wallet


# ---------------------------------------------------------------------------
class WalletCRUD(BaseCRUD[Wallet, None, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        wallet_id: UUID,
    ) -> Type[Wallet] | WalletNotFoundException:
        """
        ! Verify Wallet Existence

        Parameters
        ----------
        db
            Target database connection
        wallet_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        WalletNotFoundException
        """
        obj = await db.get(entity=self.model, ident=wallet_id)
        if not obj:
            raise WalletNotFoundException()

        return obj

    async def verify_by_user_id(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> Wallet | WalletNotFoundException:
        """
        ! Verify Wallet Existence By user id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target User ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        WalletNotFoundException
        """
        response = await db.execute(select(self.model).where(Wallet.user_id == user_id))

        obj = response.scalar_one_or_none()
        if not obj:
            raise WalletNotFoundException()

        return obj

    async def find_by_user_id(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> Wallet | WalletNotFoundException:
        """
        ! Find wallet by user id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target User ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        WalletNotFoundException
        """
        response = await db.execute(select(self.model).where(Wallet.user_id == user_id))

        obj = response.scalar_one_or_none()
        if not obj:
            raise WalletNotFoundException()

        return obj

    async def find_by_number(self, *, db: AsyncSession, number: int) -> Type[Wallet]:
        """
        ! Find Wallet by number

        Parameters
        ----------
        db
            Target database connection
        number
            Target wallet number

        Returns
        -------
        found_item
            Found Item
        """
        response = await db.execute(
            select(self.model).where(self.model.number == number),
        )

        found_item = response.scalar_one_or_none()
        return found_item

    async def generate_wallet_number(self, *, db: AsyncSession) -> int:
        """
        ! Generate wallet number

        Parameters
        ----------
        db
            Target database connection

        Returns
        -------
        code
            generated number
        """
        number = 0
        while not number:
            generate_number = randint(100000, 999999)
            is_duplicate = await self.find_by_number(db=db, number=generate_number)
            if not is_duplicate:
                number = generate_number

        return number


# ---------------------------------------------------------------------------
wallet = WalletCRUD(Wallet)
