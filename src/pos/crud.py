from typing import Type
from uuid import UUID

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
    async def verify_existence(self, *, db: AsyncSession, pos_id: UUID) -> Type[Pos]:
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

    async def verify_duplicate_number(self, *, db: AsyncSession, number: str) -> Pos:
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

    async def find_by_number(self, *, db: AsyncSession, number: str) -> Pos:
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
            raise PosNotFoundException()

        return obj


# ---------------------------------------------------------------------------
pos = PosCRUD(Pos)
