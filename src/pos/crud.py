from random import randint
from typing import Type
from uuid import UUID

import jdatetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.pos.exception import (
    PosNotFoundException,
    PosNumberIsDuplicatedException,
)
from src.pos.models import Pos
from src.pos.schema import PosCreate, PosUpdate


# ---------------------------------------------------------------------------
class PosCRUD(BaseCRUD[Pos, PosCreate, PosUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        pos_id: UUID,
    ) -> Type[Pos] | PosNotFoundException:
        """
        ! Verify Pos Existence

        Parameters
        ----------
        db
            Target database connection
        pos_id
            Target pos's ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        PosNotFoundException
        """
        obj = await db.get(entity=self.model, ident=pos_id)
        if not obj:
            raise PosNotFoundException()

        return obj

    async def verify_duplicate_number(
        self,
        *,
        db: AsyncSession,
        number: str,
    ) -> Pos | PosNumberIsDuplicatedException:
        """
        ! Verify pos code duplicated

        Parameters
        ----------
        db
            Target database connection
        number
            Target Item number

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        PosTokenIsDuplicatedException
        """
        response = await db.execute(
            select(self.model).where(self.model.number == number),
        )

        obj = response.scalar_one_or_none()
        if obj:
            raise PosNumberIsDuplicatedException()

        return obj

    async def find_by_number(
        self,
        *,
        db: AsyncSession,
        number: str,
    ) -> Pos | PosNotFoundException:
        """
        ! Verify pos existence by number

        Parameters
        ----------
        db
            Target database connection
        number
            Target Item number

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        PosNotFoundException
        """
        response = await db.execute(
            select(self.model).where(self.model.number == number),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise PosNotFoundException(time=str(jdatetime.datetime.now()))

        return obj

    async def find_by_number_v2(self, *, db: AsyncSession, number: int) -> Type[Pos]:
        """
        ! Find Pos by number

        Parameters
        ----------
        db
            Target database connection
        number
            Target Pos number

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
        ! Generate Pos number

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
            is_duplicate = await self.find_by_number_v2(db=db, number=generate_number)
            if not is_duplicate:
                number = generate_number

        return number


# ---------------------------------------------------------------------------
pos = PosCRUD(Pos)
