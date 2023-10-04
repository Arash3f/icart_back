from typing import Type
from uuid import UUID

from sqlalchemy import func, select, or_
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

    async def get_transaction_count(
        self,
        *,
        db: AsyncSession,
        wallet_id: UUID,
    ) -> bool:
        """
        ! Get Transaction Count from wallet id

        Parameters
        ----------
        db
            Target database connection
        wallet_id
            Target wallet ID

        Returns
        -------
        obj
            calculated data
        """
        transaction_count = await db.execute(
            select(func.count())
            .select_from(self.model)
            .where(
                or_(
                    self.model.transferor_id == wallet_id,
                    self.model.receiver_id == wallet_id,
                ),
            ),
        )
        transaction_count = transaction_count.scalar()

        return transaction_count

    async def get_income(
        self,
        *,
        db: AsyncSession,
        wallet_id: UUID,
    ) -> int:
        response = await db.execute(
            select(func.sum(Transaction.value))
            .select_from(Transaction)
            .filter(
                Transaction.receiver_id == wallet_id,
            ),
        )
        income = response.scalar()

        return income


# ---------------------------------------------------------------------------
transaction = TransactionCRUD(Transaction)
