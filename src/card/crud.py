from typing import Type
from uuid import UUID

import jdatetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.card.exception import CardNotFoundException, UserCardDuplicateException
from src.card.models import Card
from src.card.schema import CardUpdatePassword, CreateCard
from src.database.base_crud import BaseCRUD
from src.user.models import User
from src.utils.card_number import CardType


# ---------------------------------------------------------------------------
class CardCRUD(BaseCRUD[Card, CreateCard, CardUpdatePassword]):
    async def verify_existence(self, *, db: AsyncSession, card_id: UUID) -> Type[Card]:
        """
        ! Verify Card Existence

        Parameters
        ----------
        db
            Target database connection
        card_id
            Target card's ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        CardNotFoundException
        """
        obj = await db.get(entity=self.model, ident=card_id)
        if not obj:
            raise CardNotFoundException()

        return obj

    async def verify_by_number(self, *, db: AsyncSession, number: str) -> Card:
        """
        ! Verify Existence By Number

        Parameters
        ----------
        db
            Target database connection
        number
            Target Card Number

        Returns
        -------
        card
            Found Item

        Raises
        ------
        CardNotFoundException
        """
        response = await db.execute(
            select(self.model).where(self.model.number == number),
        )

        card_obj = response.scalar_one_or_none()
        if not card_obj:
            raise CardNotFoundException(time=str(jdatetime.datetime.now()))

        return card_obj

    async def verify_existence_with_type(
        self,
        *,
        db: AsyncSession,
        user: User,
        card_type: CardType,
    ) -> bool:
        """
        ! Verify user have card with type

        Parameters
        ----------
        db
            Target database connection
        user
            Target User
        card_type
            Target Card Type

        Returns
        -------
        res
            Result of operation

        Raises
        ------
        UserCardDuplicateException
        """
        response = await db.execute(
            select(self.model).where(
                Card.wallet == user.wallet,
                self.model.type == card_type,
            ),
        )

        card_obj = response.scalar_one_or_none()
        if card_obj:
            raise UserCardDuplicateException()

        return True

    async def find_by_number(self, *, db: AsyncSession, number: str) -> Card | None:
        """
        ! Find card By Number

        Parameters
        ----------
        db
            Target database connection
        number
            Target Card Number

        Returns
        -------
        card
            Found Item

        Raises
        ------
        CardNotFoundException
        """
        response = await db.execute(
            select(self.model).where(self.model.number == number),
        )

        card_obj = response.scalar_one_or_none()

        return card_obj


# ---------------------------------------------------------------------------
card = CardCRUD(Card)
