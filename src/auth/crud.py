from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schema import AccessToken
from src.cash.models import Cash
from src.core.config import settings
from src.core.security import generate_access_token, verify_password
from src.credit.models import Credit
from src.database.base_crud import BaseCRUD
from src.user.crud import user as user_crud
from src.user.models import User
from src.wallet.models import Wallet
from src.wallet.crud import wallet as wallet_crud


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
        # * Verify password
        verify_pass = verify_password(password, user.password)
        if not verify_pass:
            return None
        return user

    async def authenticate_by_one_time_password(
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
        user: User | None = await user_crud.find_by_username(db=db, username=username)
        if not user:
            return None
        # * Verify password
        verify_pass = verify_password(password, user.one_time_password)
        if not verify_pass:
            return None
        return user

    async def generate_access_token(
        self,
        user: User,
    ) -> AccessToken:
        """
        ! Generate access token for user

        Parameters
        ----------
        user
            Target user

        Returns
        -------
        access_token
            User access token
        """
        access_token_expire_time = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)

        token = generate_access_token(
            data={"username": user.username, "role": user.role.name},
            expire_delta=access_token_expire_time,
        )
        access_token: AccessToken = AccessToken(access_token=token, token_type="bearer")
        return access_token

    async def create_new_user(
        self,
        db: AsyncSession,
        user: User,
    ) -> AccessToken:
        """
        ! Create new user

        Parameters
        ----------
        user
            New User Data

        Returns
        -------
        user
            Created User
        """
        # ? Create Credit
        credit = Credit(
            user=user,
        )

        # ? Create Cash
        cash = Cash(
            user=user,
        )

        # ? Create Wallet
        wallet_number = await wallet_crud.generate_wallet_number(db=db)
        wallet = Wallet(
            user=user,
            number=wallet_number,
        )

        db.add(user)
        db.add(credit)
        db.add(cash)
        db.add(wallet)
        await db.commit()
        await db.refresh(user)
        return user


# ---------------------------------------------------------------------------
auth = AuthCRUD(User)
