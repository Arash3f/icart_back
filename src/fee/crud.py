from typing import Type
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.exception import InCorrectDataException
from src.fee.exception import (
    FeeIsDuplicatedException,
    FeeNotFoundException,
)
from src.fee.models import Fee, FeeTypeEnum, FeeUserType
from src.fee.schema import FeeCreate, FeeUpdate


# ---------------------------------------------------------------------------
class FeeCRUD(BaseCRUD[Fee, FeeCreate, FeeUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        fee_id: UUID,
    ) -> Type[Fee] | FeeNotFoundException:
        """
        ! Verify Fee Existence

        Parameters
        ----------
        db
            Target database connection
        fee_id
            Target fee's ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        FeeNotFoundException
        """
        obj = await db.get(entity=self.model, ident=fee_id)
        if not obj:
            raise FeeNotFoundException()

        return obj

    async def verify_duplicate_limit(
        self,
        *,
        db: AsyncSession,
        limit: int,
        value_type: FeeTypeEnum,
        user_type: FeeUserType,
        is_percentage: bool,
        exception_limit: int = None,
        exception_user_type: FeeUserType = None,
        exception_value_type: FeeTypeEnum = None,
        exception_is_percentage: bool = None,
    ) -> Fee | FeeIsDuplicatedException:
        """
        ! Verify fee limit duplicate

        Parameters
        ----------
        db
            Target database connection
        limit
            Target Item limit
        value_type
            Target value type
        user_type
            Target fee user type
        is_percentage
            fee user percentage or value
        exception_limit
            Exception fee limit
        exception_user_type
        exception_value_type
        exception_is_percentage

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        FeeIsDuplicatedException
        """
        query = select(self.model).where(
            and_(
                self.model.limit == limit,
                self.model.limit != exception_limit,
                self.model.type == value_type,
                self.model.type != exception_value_type,
                self.model.user_type == user_type,
                self.model.user_type != exception_user_type,
            ),
        )
        if is_percentage and is_percentage != exception_is_percentage:
            query = query.filter(
                self.model.value.is_(None),
            )
        elif not is_percentage and is_percentage != exception_is_percentage:
            query = query.filter(
                self.model.percentage.is_(None),
            )
        response = await db.execute(
            query,
        )

        obj = response.scalar_one_or_none()
        if obj:
            raise FeeIsDuplicatedException()

        return obj

    async def calculate_fee(
        self,
        db: AsyncSession,
        amount: int,
        value_type: FeeTypeEnum,
        user_type: FeeUserType,
    ) -> int:
        """
        ! Calculate Fee

        Parameters
        ----------
        db
            database connection
        amount
            value of transaction
        value_type
            type of value
        user_type
            type of user

        Returns
        -------
        response
            fee of value
        """
        fee_response = await db.execute(
            select(self.model)
            .order_by(self.model.limit.asc())
            .where(
                self.model.limit >= amount,
                self.model.type == value_type,
                self.model.user_type == user_type,
            ),
        )

        target_fee = fee_response.scalars().first()
        if target_fee:
            if target_fee.percentage:
                fee_value = int((amount * target_fee.percentage) / 100)
            elif target_fee.value:
                fee_value = target_fee.value
        else:
            if value_type == FeeTypeEnum.CREDIT:
                fee_value = int((amount * 0.3) / 100)
            elif value_type == FeeTypeEnum.CASH:
                fee_value = int((amount * 0.3) / 100)
            else:
                raise InCorrectDataException()

        return fee_value


# ---------------------------------------------------------------------------
fee = FeeCRUD(Fee)
