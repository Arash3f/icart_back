import enum
from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cash.exception import CashNotFoundException
from src.cash.models import Cash
from src.database.base_crud import BaseCRUD


class TypeOperation(enum.Enum):
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"


class CashField(enum.Enum):
    BALANCE = "OPEN"
    RECEIVED = "RECEIVED"
    CONSUMED = "CONSUMED"
    TRANSFERRED = "TRANSFERRED"
    DEPT = "DEPT"


# ---------------------------------------------------------------------------
class CashCRUD(BaseCRUD[Cash, None, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        cash_id: UUID,
    ) -> Type[Cash] | CashNotFoundException:
        """
        Verify object exist by id

        Parameters
        ----------
        db
            database connection
        cash_id
            cash object id

        Returns
        -------
        obj
            found object

        Raises
        ------
        CashNotFoundException
        """
        obj = await db.get(entity=self.model, ident=cash_id)
        if not obj:
            raise CashNotFoundException()

        return obj

    async def find_by_user_id(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> Cash | CashNotFoundException:
        """
        ! Verify cash existence by user's id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target user's id

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        CashNotFoundException
        """
        response = await db.execute(
            select(self.model).where(self.model.user.id == user_id),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise CashNotFoundException()

        return obj

    async def update_cash_balance_by_user_id(
        self,
        *,
        db: AsyncSession,
        type_operation: TypeOperation,
        cash_field: CashField,
        user_id: UUID,
        amount: int,
    ) -> bool | CashNotFoundException:
        """
        Complete section for update user cash record

        Parameters
        ----------
        db
            database connection
        type_operation
            type of operation -> + or -
        cash_field
            which field must update?
        user_id
            target user id
        amount
            balance value

        Returns
        -------
        response
            result of operation

        Raises
        ------
        CashNotFoundException
        """
        response = await db.execute(
            select(self.model).where(self.model.user.id == user_id),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise CashNotFoundException()

        match cash_field:
            case CashField.BALANCE:
                if type_operation == TypeOperation.DECREASE:
                    obj.balance -= amount
                else:
                    obj.balance += amount

            case CashField.TRANSFERRED:
                if type_operation == TypeOperation.DECREASE:
                    obj.transferred -= amount
                else:
                    obj.transferred += amount

            case CashField.DEPT:
                if type_operation == TypeOperation.DECREASE:
                    obj.debt -= amount
                else:
                    obj.debt += amount

            case CashField.RECEIVED:
                if type_operation == TypeOperation.DECREASE:
                    obj.received -= amount
                else:
                    obj.received += amount

            case CashField.CONSUMED:
                if type_operation == TypeOperation.DECREASE:
                    obj.consumed -= amount
                else:
                    obj.consumed += amount

        db.add(obj)
        await db.commit()

        return True


# ---------------------------------------------------------------------------
cash = CashCRUD(Cash)
