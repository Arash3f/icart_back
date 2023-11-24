from typing import Type
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.band_card.exception import BankCardNotFound
from src.band_card.models import BankCard
from src.band_card.schemas import BankCardCreate, BankCardUpdate
from src.database.base_crud import BaseCRUD
from src.user.models import User


# ----------------------------------------------------------------
class BankCardCRUD(BaseCRUD[BankCard, BankCardCreate, BankCardUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        bank_card_id: UUID,
    ) -> Type[BankCard] | BankCardNotFound:
        """
        ! Verify BankCard Existence

        Parameters
        ----------
        db
            Target database connection
        bank_card_id
            Target BankCard's ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        BankCardNotFound
        """
        obj = await db.get(entity=self.model, ident=bank_card_id)
        if not obj:
            raise BankCardNotFound()

        return obj

    async def verify_existence_by_id_and_user_id(
        self,
        *,
        db: AsyncSession,
        bank_card_id: UUID,
        user_id: UUID,
    ) -> Type[BankCard] | BankCardNotFound:
        """
         ! Verify Bank card Existence by id and user_id

        Parameters
        ----------
        db
            Target database connection
        bank_card_id
            Target bank card's id
        user_id
            Target user id

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        BankCardNotFound
        """
        res = await db.execute(
            select(self.model).where(
                self.model.id == bank_card_id,
                self.model.user_id == user_id,
            ),
        )
        obj = res.scalar_one_or_none()
        if not obj:
            raise BankCardNotFound()

        return obj

    async def find_by_id_and_user_id(
        self,
        *,
        db: AsyncSession,
        bank_card_id: UUID,
        user_id: UUID,
    ) -> Type[BankCard] | BankCardNotFound | None:
        """
         ! Find bank card by id and user_id

        Parameters
        ----------
        db
            Target database connection
        bank_card_id
            Target bank card's id
        user_id
            Target user id

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        BankCardNotFound
        """
        res = await db.execute(
            select(self.model).where(
                self.model.id == bank_card_id,
                self.model.user_id == user_id,
            ),
        )
        obj = res.scalar_one_or_none()
        return obj

    async def verify_existence_by_bank_card_number(
        self,
        *,
        db: AsyncSession,
        card_number: str,
    ) -> Type[BankCard] | BankCardNotFound:
        """
         ! Verify Bank card Existence by bank card number

        Parameters
        ----------
        db
            Target database connection
        card_number
            Target bank card number

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        BankCardNotFound
        """
        res = await db.execute(
            select(self.model).where(
                self.model.card_number == card_number,
            ),
        )
        obj = res.scalar_one_or_none()
        if not obj:
            raise BankCardNotFound()

        return obj

    async def find_by_bank_card_number(
        self,
        *,
        db: AsyncSession,
        card_number: str,
    ) -> Type[BankCard] | BankCardNotFound:
        """
         ! Verify Bank card Existence by bank card number

        Parameters
        ----------
        db
            Target database connection
        card_number
            Target bank card number

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        BankCardNotFound
        """
        res = await db.execute(
            select(self.model).where(
                self.model.card_number == card_number,
            ),
        )
        obj = res.scalar_one_or_none()
        return obj


# ----------------------------------------------------------------
bank_card = BankCardCRUD(BankCard)
