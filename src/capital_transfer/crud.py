from typing import Type
from uuid import UUID

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


# ---------------------------------------------------------------------------
capital_transfer = CapitalTransferCRUD(CapitalTransfer)
