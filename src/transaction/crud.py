from typing import Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.transaction.exception import TransactionNotFoundException
from src.transaction.models import Transaction
from src.transaction.schema import TransactionCreate


# ---------------------------------------------------------------------------
class TransactionCRUD(BaseCRUD[Transaction, TransactionCreate, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        transaction_id: UUID,
    ) -> Type[Transaction]:
        """
        ! Verify Transaction Existence

        Parameters
        ----------
        db
            Target database connection
        transaction_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        TransactionNotFoundException
        """
        obj = await db.get(entity=self.model, ident=transaction_id)
        if not obj:
            raise TransactionNotFoundException()

        return obj


# ---------------------------------------------------------------------------
transaction = TransactionCRUD(Transaction)
