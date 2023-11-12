from typing import Type
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.verify_phone.exception import (
    IncorrectCodeException,
    VerifyPhoneNotFoundException,
)
from src.verify_phone.models import VerifyPhone


# ---------------------------------------------------------------------------
class VerifyPhoneCRUD(BaseCRUD[VerifyPhone, None, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        verify_phone_id: UUID,
    ) -> Type[VerifyPhone] | VerifyPhoneNotFoundException:
        """
        ! Verify Existence

        Parameters
        ----------
        db
            Target database connection
        verify_phone_id
            Target Item ID

        Returns
        -------
        found_item
            Found Item

        Raises
        ------
        VerifyPhoneNotFoundException
            Verify Phone with this id not exist
        """
        found_item = await db.get(entity=self.model, ident=verify_phone_id)
        if not found_item:
            raise VerifyPhoneNotFoundException()

        return found_item

    async def find_by_phone_number(
        self,
        *,
        db: AsyncSession,
        phone_number: str,
    ) -> Type[VerifyPhone]:
        """
        ! Find Verify Phone by phone number

        Parameters
        ----------
        db
            Target database connection
        phone_number
            Target phone number

        Returns
        -------
        found_item
            Found Item

        """
        response = await db.execute(
            select(self.model).where(self.model.phone_number == phone_number),
        )

        found_item = response.scalar_one_or_none()
        return found_item

    async def find_by_verify_code(
        self,
        *,
        db: AsyncSession,
        verify_code: int,
    ) -> Type[VerifyPhone]:
        """
        ! Find Verify Phone by phone number

        Parameters
        ----------
        db
            Target database connection
        verify_code
            Target verify code

        Returns
        -------
        found_item
            Found Item

        """
        response = await db.execute(
            select(self.model).where(self.model.verify_code == verify_code),
        )

        found_item = response.scalar_one_or_none()
        return found_item

    async def verify_with_verify_code(
        self,
        *,
        db: AsyncSession,
        phone_number: str,
        verify_code: int,
    ) -> Type[VerifyPhone] | IncorrectCodeException:
        """
        ! Verify Phone code with code

        Parameters
        ----------
        db
            Target database connection
        verify_code
            Target verify code
        phone_number
            Target phone number

        Returns
        -------
        found_item
            Found Item

        Raises
        ------
        IncorrectCodeException
        """
        response = await db.execute(
            select(self.model).where(
                and_(
                    self.model.phone_number == phone_number,
                    self.model.verify_code == verify_code,
                ),
            ),
        )

        found_item = response.scalar_one_or_none()
        if not found_item:
            raise IncorrectCodeException()
        return found_item


# ---------------------------------------------------------------------------
verify_phone = VerifyPhoneCRUD(VerifyPhone)
