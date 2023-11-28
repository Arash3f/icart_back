from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.user_request.exception import UserRequestNotFoundException
from src.user_request.models import UserRequest
from src.user_request.schema import CreateUserRequest, UpdateUserRequest


# ---------------------------------------------------------------------------
class UserRequestCRUD(BaseCRUD[UserRequest, CreateUserRequest, UpdateUserRequest]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        user_request_id: UUID,
    ) -> Type[UserRequest]:
        """
        ! Verify user request existence with id

        Parameters
        ----------
        db
            Target database connection
        user_request_id
            Target User's request id

        Returns
        -------
        user
            Found user

        Raises
        -----
        UserRequestNotFoundException
        """
        obj = await db.get(entity=self.model, ident=user_request_id)
        if not obj:
            raise UserRequestNotFoundException()

        return obj

    async def verify_existence_by_user_id(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> Type[UserRequest]:
        """
        ! Verify user request existence with user id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target User's request id

        Returns
        -------
        found_item
            Found user request

        Raises
        ------
        UserRequestNotFoundException
        """
        response = await db.execute(
            select(self.model).where(self.model.user_id == user_id),
        )

        found_item = response.scalar_one_or_none()
        if not found_item:
            raise UserRequestNotFoundException()
        return found_item

    async def find_by_user_id(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> Type[UserRequest]:
        """
        ! Verify user request existence with user id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target User's request id

        Returns
        -------
        found_item
            Found user request
        """
        response = await db.execute(
            select(self.model).filter(self.model.user_id == user_id),
        )

        found_item = response.scalar_one_or_none()
        return found_item


# ---------------------------------------------------------------------------
user_request = UserRequestCRUD(UserRequest)
