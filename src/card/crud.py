from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.card.exception import CardNotFoundException
from src.card.models import Card
from src.card.schema import CardUpdatePassword
from src.database.base_crud import BaseCRUD


# ---------------------------------------------------------------------------
class CardCRUD(BaseCRUD[Card, None, CardUpdatePassword]):
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
            raise CardNotFoundException()

        return card_obj


# ---------------------------------------------------------------------------
card = CardCRUD(Card)
