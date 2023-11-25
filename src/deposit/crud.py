from typing import Type
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.deposit.exception import DepositNotFound
from src.deposit.models import Deposit
from src.deposit.schemas import DepositCreate
from src.database.base_crud import BaseCRUD


# ---------------------------------------------------------------------------
class DepositCRUD(BaseCRUD[Deposit, DepositCreate, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        deposit_id: UUID,
    ) -> Type[Deposit] | DepositNotFound:
        """
        ! Verify Deposit Existence

        Parameters
        ----------
        db
            Target database connection
        deposit_id
            Target Deposit ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        DepositNotFound
        """
        obj = await db.get(entity=self.model, ident=deposit_id)
        if not obj:
            raise DepositNotFound()

        return obj


# ---------------------------------------------------------------------------
deposit = DepositCRUD(Deposit)
