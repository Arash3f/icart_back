from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import verify_password
from src.database.base_crud import BaseCRUD
from src.user.crud import user as user_crud
from src.user.models import User


# ---------------------------------------------------------------------------
class AuthCRUD(BaseCRUD[User, None, None]):
    async def authenticate(
        self,
        db: AsyncSession,
        username: str,
        password: str,
    ) -> User | None:
        """
        ! Verify user with password

        Parameters
        ----------
        db
            Target database connection
        username
            Target Username
        password
            Target Password

        Returns
        -------
        user
            Found user or None
        """
        user = await user_crud.find_by_username(db=db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def authenticate_v2(
        self,
        db: AsyncSession,
        username: str,
        password: str,
    ) -> User | None:
        """
        ! Verify user with one time password

        Parameters
        ----------
        db
            Target database connection
        username
            Target Username
        password
            Target One Time Password

        Returns
        -------
        user
            Found user or None
        """
        user: User | None = await user_crud.get_by_username(db=db, username=username)
        if not user:
            return None
        if not user.one_time_password == password:
            return None
        return user


# ---------------------------------------------------------------------------
auth = AuthCRUD(User)
