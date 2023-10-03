from random import randint
from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.capital_transfer.exception import CapitalTransferNotFoundException
from src.capital_transfer.models import CapitalTransfer
from src.capital_transfer.schema import CapitalTransferCreate
from src.database.base_crud import BaseCRUD


# ---------------------------------------------------------------------------
class CapitalTransferCRUD(BaseCRUD[CapitalTransfer, CapitalTransferCreate, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        capital_transfer_id: UUID,
    ) -> Type[CapitalTransfer]:
        """
        ! Verify CapitalTransfer Existence

        Parameters
        ----------
        db
            Target database connection
        capital_transfer_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        CapitalTransferNotFoundException
        """
        obj = await db.get(entity=self.model, ident=capital_transfer_id)
        if not obj:
            raise CapitalTransferNotFoundException()

        return obj

    async def find_by_code(
        self,
        *,
        db: AsyncSession,
        code: int,
    ) -> Type[CapitalTransfer]:
        """
        ! Find Capital Transfer by code

        Parameters
        ----------
        db
            Target database connection
        code
            Capital Transfer code

        Returns
        -------
        found_item
            Found Item
        """
        response = await db.execute(
            select(self.model).where(self.model.code == code),
        )

        found_item = response.scalar_one_or_none()
        return found_item

    async def generate_code(self, *, db: AsyncSession) -> int:
        """
        ! Generate code

        Parameters
        ----------
        db
            Target database connection

        Returns
        -------
        code
            generated code
        """
        code = 0
        while not code:
            generate_code = randint(100000, 999999)
            is_duplicate = await self.find_by_code(db=db, code=generate_code)
            if not is_duplicate:
                code = generate_code

        return code


# ---------------------------------------------------------------------------
capital_transfer = CapitalTransferCRUD(CapitalTransfer)
