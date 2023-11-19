from datetime import datetime, timezone, timedelta
from random import randint
from typing import Type
from uuid import UUID

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.transaction.exception import TransactionNotFoundException
from src.transaction.models import Transaction, TransactionRow
from src.transaction.schema import TransactionCreate, TransactionRowCreate
from src.user.models import User


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
                    self.model.transferor.mapper.class_.wallet_id == wallet_id,
                    self.model.receiver.mapper.class_.wallet_id == wallet_id,
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
                Transaction.receiver.mapper.class_.wallet_id == wallet_id,
            ),
        )
        income = response.scalar_one_or_none()

        return income

    async def find_by_code(
        self,
        *,
        db: AsyncSession,
        code: int,
    ) -> Type[TransactionRow]:
        """
        ! Find Transaction by code

        Parameters
        ----------
        db
            Target database connection
        code
            Capital transaction row code

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
class TransactionRowCRUD(BaseCRUD[TransactionRow, TransactionRowCreate, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        transaction_row_id: UUID,
    ) -> Type[TransactionRow]:
        """
        ! Verify Transaction Existence

        Parameters
        ----------
        db
            Target database connection
        transaction_row_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        TransactionNotFoundException
        """
        obj = await db.get(entity=self.model, ident=transaction_row_id)
        if not obj:
            raise TransactionNotFoundException()

        return obj

    async def find_by_code(
        self,
        *,
        db: AsyncSession,
        code: int,
    ) -> Type[TransactionRow]:
        """
        ! Find Transaction row by code

        Parameters
        ----------
        db
            Target database connection
        code
            Capital transaction row code

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

    async def calculate_user_amount_transaction(
        self,
        *,
        db: AsyncSession,
        user: User,
        min: int,
    ) -> int:
        start = datetime.now()
        end = start - timedelta(
            minutes=min,
        )
        my_query = await db.execute(
            select(func.sum(self.model.value))
            .select_from(self.model)
            .where(
                self.model.transferor.mapper.class_.wallet == user.wallet,
                self.model.created_at <= start,
                self.model.created_at >= end,
            ),
        )

        response = my_query.scalar()
        return response


# ---------------------------------------------------------------------------
transaction = TransactionCRUD(Transaction)
transaction_row = TransactionRowCRUD(TransactionRow)
