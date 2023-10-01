from random import randint
from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.verify_phone.exception import VerifyPhoneNotFoundException
from src.verify_phone.models import VerifyPhone


# ---------------------------------------------------------------------------
class VerifyPhoneCRUD(BaseCRUD[VerifyPhone, None, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        verify_phone_id: UUID,
    ) -> Type[VerifyPhone]:
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

    async def generate_dynamic_code(self, *, db: AsyncSession) -> int:
        """
        ! Generate dynamic code

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
            is_duplicate = await self.find_by_verify_code(
                db=db,
                verify_code=generate_code,
            )
            if not is_duplicate:
                code = generate_code

        return code


# ---------------------------------------------------------------------------
verify_phone = VerifyPhoneCRUD(VerifyPhone)
