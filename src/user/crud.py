from typing import Type
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exception import ReferralCodeDoesNotExistException
from src.database.base_crud import BaseCRUD
from src.user.exception import (
    NationalCodeIsDuplicatedException,
    UsernameIsDuplicatedException,
    UserNotFoundException,
    UsernameOrNationalCodeIsDuplicatedException,
)
from src.user.models import User
from src.important_data.crud import important_data as important_data_crud


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

    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> Type[User] | UserNotFoundException:
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
    ) -> Type[User] | UsernameOrNationalCodeIsDuplicatedException:
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
            raise UsernameOrNationalCodeIsDuplicatedException()

        return user

    async def verify_duplicate_username(
        self,
        *,
        db: AsyncSession,
        username: str,
        exception_username: str = None,
    ) -> User | UsernameIsDuplicatedException:
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

    async def verify_by_icart_member_number(
        self,
        *,
        db: AsyncSession,
        icart_member_number: str,
    ) -> User | UserNotFoundException:
        """
        ! Verify by icart member number

        Parameters
        ----------
        db
            Target database connection
        icart_member_number
            Target number

        Returns
        -------
        user
            Found user

        Raises
        ------
        UserNotFoundException
        """
        response = await db.execute(
            select(self.model).where(
                User.icart_member_number == icart_member_number,
            ),
        )

        user = response.scalar_one_or_none()
        if user:
            raise UserNotFoundException()

        return user

    async def verify_duplicate_national_code(
        self,
        *,
        db: AsyncSession,
        national_code: str,
        exception_national_code: str = None,
    ) -> User | NationalCodeIsDuplicatedException:
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
    ) -> User | UserNotFoundException:
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

    async def verify_existence_by_national_number(
        self,
        *,
        db: AsyncSession,
        national_code: str,
    ) -> User | UserNotFoundException:
        """
        ! Verify user existence by national number
        Parameters
        ----------
        db
            database connection
        national_code
            Target user national code

        Returns
        -------
        res
            found user

        Raises
        ------
        UserNotFoundException
        """
        res = await db.execute(
            select(self.model).where(self.model.national_code == national_code),
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
    ) -> Type[User] | UsernameIsDuplicatedException:
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

    async def check_by_username_and_national_code(
        self,
        *,
        db: AsyncSession,
        username=str,
        national_code=str,
    ) -> Type[User] | None:
        """
        ! Check with username & national code

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
            Found user | None
        """
        response = await db.execute(
            select(self.model).where(
                and_(User.username == username, User.national_code == national_code),
            ),
        )

        user = response.scalar_one_or_none()

        return user

    async def check_by_username_or_national_code(
        self,
        *,
        db: AsyncSession,
        username=str,
        national_code=str,
    ) -> Type[User] | None:
        """
        ! Check with username Or national code

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
            Found user | None
        """
        response = await db.execute(
            select(self.model).where(
                or_(User.username == username, User.national_code == national_code),
            ),
        )

        user = response.scalar_one_or_none()

        return user

    async def find_by_referral_code(
        self,
        db: AsyncSession,
        referral_code: str,
    ) -> Type[User] | None:
        result = await db.execute(
            select(self.model).where(self.model.referral_code == referral_code),
        )
        return result.scalar_one_or_none()

    async def verify_existence_by_referral_code(
        self,
        db: AsyncSession,
        referral_code: str,
    ) -> Type[User] | None:
        result = await db.execute(
            select(self.model).where(self.model.referral_code == referral_code),
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ReferralCodeDoesNotExistException()

        return user

    async def find_referral_icart_member(self, db: AsyncSession) -> User:
        important_data = await important_data_crud.get_last_obj(db=db)
        target_member = important_data.referral_user_number
        member = await self.verify_by_icart_member_number(
            db=db,
            icart_member_number=target_member,
        )
        return member


# ---------------------------------------------------------------------------
user = UserCRUD(User)
