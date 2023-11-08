import enum
from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.credit.exception import CreditNotFoundException
from src.credit.models import Credit
from src.database.base_crud import BaseCRUD


class TypeOperation(enum.Enum):
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"


class CreditField(enum.Enum):
    BALANCE = "OPEN"
    RECEIVED = "RECEIVED"
    CONSUMED = "CONSUMED"
    TRANSFERRED = "TRANSFERRED"
    DEPT = "DEPT"


# ---------------------------------------------------------------------------
class CreditCRUD(BaseCRUD[Credit, None, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        credit_id: UUID,
    ) -> Type[Credit] | CreditNotFoundException:
        """
        Verify object exist by id

        Parameters
        ----------
        db
            database connection
        credit_id
            credit object id

        Returns
        -------
        obj
            found object

        Raises
        ------
        CreditNotFoundException
        """
        obj = await db.get(entity=self.model, ident=credit_id)
        if not obj:
            raise CreditNotFoundException()

        return obj

    async def find_by_user_id(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> Credit | CreditNotFoundException:
        """
        ! Verify credit existence by user's id

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
        CreditNotFoundException
        """
        response = await db.execute(
            select(self.model).where(self.model.user.id == user_id),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise CreditNotFoundException()

        return obj

    async def update_credit_balance_by_user_id(
        self,
        *,
        db: AsyncSession,
        type_operation: TypeOperation,
        credit_field: CreditField,
        user_id: UUID,
        amount: int,
    ) -> bool | CreditNotFoundException:
        """
        Complete section for update user credit record

        Parameters
        ----------
        db
            database connection
        type_operation
            type of operation -> + or -
        credit_field
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
        CreditNotFoundException
        """
        response = await db.execute(
            select(self.model).where(self.model.user.id == user_id),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise CreditNotFoundException()

        match credit_field:
            case CreditField.BALANCE:
                if type_operation == TypeOperation.DECREASE:
                    obj.balance -= amount
                else:
                    obj.balance += amount

            case CreditField.TRANSFERRED:
                if type_operation == TypeOperation.DECREASE:
                    obj.transferred -= amount
                else:
                    obj.transferred += amount

            case CreditField.DEPT:
                if type_operation == TypeOperation.DECREASE:
                    obj.debt -= amount
                else:
                    obj.debt += amount

            case CreditField.RECEIVED:
                if type_operation == TypeOperation.DECREASE:
                    obj.received -= amount
                else:
                    obj.received += amount

            case CreditField.CONSUMED:
                if type_operation == TypeOperation.DECREASE:
                    obj.consumed -= amount
                else:
                    obj.consumed += amount

        db.add(obj)
        await db.commit()

        return True


# ---------------------------------------------------------------------------
credit = CreditCRUD(Credit)
