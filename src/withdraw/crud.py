from typing import Type
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.withdraw.exception import WithdrawNotFound
from src.withdraw.models import Withdraw
from src.withdraw.schemas import WithdrawCreate, WithdrawUpdate
from src.database.base_crud import BaseCRUD


# ---------------------------------------------------------------------------
class WithdrawCRUD(BaseCRUD[Withdraw, WithdrawCreate, WithdrawUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        withdraw_id: UUID,
    ) -> Type[Withdraw] | WithdrawNotFound:
        """
        ! Verify Withdraw Existence

        Parameters
        ----------
        db
            Target database connection
        withdraw_id
            Target Withdraw ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        WithdrawNotFound
        """
        obj = await db.get(entity=self.model, ident=withdraw_id)
        if not obj:
            raise WithdrawNotFound()

        return obj


# ---------------------------------------------------------------------------
withdraw = WithdrawCRUD(Withdraw)
