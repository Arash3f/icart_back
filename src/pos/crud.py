from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.pos.exception import (
    PosNotFoundException,
    PosTokenIsDuplicatedException,
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

    async def verify_duplicate_token(self, *, db: AsyncSession, token: str) -> Pos:
        """
        ! Verify pos code duplicated

        Parameters
        ----------
        db
            Target database connection
        token
            Target Item token

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        PosTokenIsDuplicatedException
        """
        response = await db.execute(select(self.model).where(self.model.token == token))

        obj = response.scalar_one_or_none()
        if obj:
            raise PosTokenIsDuplicatedException()

        return obj


# ---------------------------------------------------------------------------
pos = PosCRUD(Pos)
