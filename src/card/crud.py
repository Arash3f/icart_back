import enum
from datetime import datetime
from typing import Type
from uuid import UUID

import jdatetime
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.card.exception import (
    CardNotFoundException,
    UserCardDuplicateException,
    UserCardIsDeActiveException,
)
from src.card.models import Card, CardEnum
from src.card.schema import CardUpdatePassword, CreateCard
from src.database.base_crud import BaseCRUD
from src.user.models import User
from src.utils.card_number import CardType
from src.wallet.crud import wallet as wallet_card
from src.wallet.models import Wallet


class CardValueType(enum.Enum):
    CASH = "CASH"
    CREDIT = "CREDIT"


# ---------------------------------------------------------------------------
class CardCRUD(BaseCRUD[Card, CreateCard, CardUpdatePassword]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        card_id: UUID,
    ) -> Type[Card] | CardNotFoundException:
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

    async def verify_by_number(
        self,
        *,
        db: AsyncSession,
        number: str,
    ) -> Card | CardNotFoundException:
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
            select(self.model).where(
                self.model.number == number,
                self.model.is_active == True,
                self.model.is_receive == True,
            ),
        )

        card_obj = response.scalar_one_or_none()
        if not card_obj:
            raise CardNotFoundException()

        return card_obj

    async def verify_by_number_v2(
        self,
        *,
        db: AsyncSession,
        number: str,
    ) -> Card | CardNotFoundException:
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
            select(self.model).where(
                self.model.number == number,
                self.model.is_active == True,
            ),
        )

        card_obj = response.scalar_one_or_none()
        if not card_obj:
            raise CardNotFoundException()

        return card_obj

    async def verify_existence_with_type(
        self,
        *,
        db: AsyncSession,
        user: User,
        card_type: CardEnum,
        is_active: bool = True,
    ) -> bool | UserCardDuplicateException:
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
        is_active
            Is card active

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
                self.model.is_active == is_active,
            ),
        )

        card_obj = response.scalar_one_or_none()
        if card_obj:
            raise UserCardDuplicateException()

        return True

    async def check_card_exp(
        self,
        *,
        db: AsyncSession,
        card_id: UUID,
    ) -> bool | UserCardIsDeActiveException:
        """
        ! Verify user card activation

        Parameters
        ----------
        db
            Target database connection
        card_id
            Target User Card

        Returns
        -------
        res
            Result of operation

        Raises
        ------
        UserCardIsDeActiveException
        """
        now = datetime.now()
        response = await db.execute(
            select(self.model).where(
                Card.id == card_id,
                Card.expiration_at >= now,
            ),
        )

        card_obj = response.scalar_one_or_none()
        if not card_obj:
            raise UserCardIsDeActiveException()

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
        """
        response = await db.execute(
            select(self.model).where(self.model.number == number),
        )

        card_obj = response.scalar_one_or_none()

        return card_obj

    async def get_active_card(
        self,
        *,
        db: AsyncSession,
        wallet: Wallet,
        card_value_type: CardValueType,
    ) -> Card | None:
        """
        ! Find active card for user

        Parameters
        ----------
        db
            Target database connection
        wallet
            Target User wallet
        card_value_type
            Target Card Type

        Returns
        -------
        card
            Found Item
        """
        type_filter = self.model.type == CardEnum.CREDIT
        if card_value_type == CardValueType.CASH:
            type_filter = or_(
                self.model.type == CardEnum.BLUE,
                self.model.type == CardEnum.GOLD,
                # self.model.type == CardEnum.SILVER,
            )

        response = await db.execute(
            select(Card).filter(
                Card.wallet == wallet,
                Card.is_active == True,
                type_filter,
            ),
        )

        card_obj = response.scalar_one_or_none()

        if card_obj is None:
            raise CardNotFoundException()

        return card_obj


# ---------------------------------------------------------------------------
card = CardCRUD(Card)
