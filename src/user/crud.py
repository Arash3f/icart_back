from typing import Type
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.user.exception import (
    NationalCodeIsDuplicatedException,
    UsernameIsDuplicatedException,
    UserNotFoundException,
)
from src.user.models import User


# ---------------------------------------------------------------------------
class UserCRUD(BaseCRUD[User, None, None]):
    async def find_by_username(self, db: AsyncSession, username: str) -> User | None:
        """
        ! Find user with username

        Parameters
        ----------
        db
            Target database connection
        username
            Target username

        Returns
        -------
        obj
            Found user or None
        """
        response = await db.execute(
            select(self.model).where(self.model.username == username),
        )
        obj = response.scalar_one_or_none()

        return obj

    async def verify_user_existence(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> Type[User]:
        """
        ! Verify user existence with id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target User's id

        Returns
        -------
        user
            Found user

        Raises
        -----
        UserNotFoundException
            can not find user with this id
        """
        obj = await db.get(entity=self.model, ident=user_id)
        if not obj:
            raise UserNotFoundException()

        return obj

    async def verify_not_existence_by_username_and_national_code(
        self,
        *,
        db: AsyncSession,
        username=str,
        national_code=str,
    ) -> Type[User]:
        """
        ! Verify user existence with username & national code

        Parameters
        ----------
        db
            Target database connection
        username
            Target User's username
        national_code
            Target User's national_code
        Returns
        -------
        user
            Found user

        Raises
        -----
        UserNotFoundException
            can not find user with this id
        """
        response = await db.execute(
            select(self.model).where(
                or_(User.username == username, User.national_code == national_code),
            ),
        )

        user = response.scalar_one_or_none()
        if user:
            raise UsernameIsDuplicatedException()

        return user

    async def verify_duplicate_username(
        self,
        *,
        db: AsyncSession,
        username: str,
        exception_username: str = None,
    ) -> User:
        """
        ! Verify username duplicate

        Parameters
        ----------
        db
            Target database connection
        username
            Target username
        exception_username
            Exception username that not be considered in filter

        Returns
        -------
        user
            Found user

        Raises
        ------
        UsernameIsDuplicatedException
            username is duplicated
        """
        response = await db.execute(
            select(self.model).where(
                and_(User.username == username, User.username != exception_username),
            ),
        )

        user = response.scalar_one_or_none()
        if user:
            raise UsernameIsDuplicatedException()

        return user

    async def verify_duplicate_national_code(
        self,
        *,
        db: AsyncSession,
        national_code: str,
        exception_national_code: str = None,
    ) -> User:
        """
        ! Verify national_code duplicate

        Parameters
        ----------
        db
            Target database connection
        national_code
            Target national_code
        exception_national_code
            Exception national_code that not be considered in filter

        Returns
        -------
        user
            Found user

        Raises
        ------
        NationalCodeIsDuplicatedException
        """
        response = await db.execute(
            select(self.model).where(
                and_(
                    User.national_code == national_code,
                    User.national_code != exception_national_code,
                ),
            ),
        )

        user = response.scalar_one_or_none()
        if user:
            raise NationalCodeIsDuplicatedException()

        return user

    async def verify_existence_by_username(
        self,
        *,
        db: AsyncSession,
        username: str,
    ) -> User:
        """
        ! Verify User Existence with username

        Parameters
        ----------
        db
            Target database connection
        username
            Target user username

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        UserNotFoundException
        """
        res = await db.execute(
            select(self.model).where(self.model.username == username),
        )
        obj = res.scalar_one_or_none()
        if not obj:
            raise UserNotFoundException()

        return obj

    async def find_by_username_and_national_code(
        self,
        *,
        db: AsyncSession,
        username=str,
        national_code=str,
    ) -> Type[User]:
        """
        ! Find with username & national code

        Parameters
        ----------
        db
            Target database connection
        username
            Target User's username
        national_code
            Target User's national_code
        Returns
        -------
        user
            Found user

        Raises
        -----
        UserNotFoundException
            can not find user with this id
        """
        response = await db.execute(
            select(self.model).where(
                and_(User.username == username, User.national_code == national_code),
            ),
        )

        user = response.scalar_one_or_none()
        if not user:
            raise UsernameIsDuplicatedException()

        return user


# ---------------------------------------------------------------------------
user = UserCRUD(User)
