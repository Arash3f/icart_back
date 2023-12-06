from typing import AsyncGenerator, Type

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exception import (
    AccessDeniedException,
    InactiveUserException,
    UserNotAuthenticatedException,
)
from src.core.config import settings
from src.database.session import SessionLocal
from src.role.crud import role as role_crud
from src.schema import VerifyUserDep
from src.user.crud import user as user_crud
from src.user.models import User
from src.utils.minio_client import MinioClient

# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# ---------------------------------------------------------------------------
class TokenData(BaseModel):
    username: str
    role: str


# ---------------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ---------------------------------------------------------------------------
def get_current_user() -> Type[User]:
    """
    ! Verify Token
    ! Find User
    ! Verify User Activity

    Returns
    -------
    user
        Found user
    """

    async def current_user(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme),
    ) -> Type[User]:
        if not token:
            raise UserNotAuthenticatedException()

        # ? Verify Token
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenData(username=payload["username"], role=payload["role"])
        # ? Verify User
        user = await user_crud.find_by_username(db=db, username=token_data.username)
        # ? Verify user activity
        if not user.is_active or not user.is_valid:
            raise InactiveUserException()
        return user

    return current_user


# ---------------------------------------------------------------------------
def get_current_user_v2() -> Type[User]:
    """
    ! Verify Token
    ! Find User
    ! Verify User Activity

    Returns
    -------
    user
        Found user
    """

    async def current_user(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme),
    ) -> Type[User]:
        if not token:
            raise UserNotAuthenticatedException()

        # ? Verify Token
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenData(username=payload["username"], role=payload["role"])
        # ? Verify User
        user = await user_crud.find_by_username(
            db=db,
            username=token_data.username,
        )
        # ? Verify user activity
        if not user.is_active:
            raise InactiveUserException()
        return user

    return current_user


# ---------------------------------------------------------------------------
def get_current_user_v3() -> Type[User]:
    """
    ! Verify Token
    ! Find User

    Returns
    -------
    user
        Found user
    """

    async def current_user(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme),
    ) -> Type[User]:
        if not token:
            raise UserNotAuthenticatedException()

        # ? Verify Token
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenData(username=payload["username"], role=payload["role"])
        # ? Verify User
        user = await user_crud.find_by_username(
            db=db,
            username=token_data.username,
        )
        return user

    return current_user


# ---------------------------------------------------------------------------
def get_current_user_with_permissions(
    required_permissions: list[int] | None = None,
) -> Type[User]:
    async def current_user_with_permissions(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme),
    ) -> Type[User]:
        if not token:
            raise UserNotAuthenticatedException()

        # ? Verify Token
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenData(username=payload["username"], role=payload["role"])

        # ? Verify User
        user = await user_crud.verify_existence_by_username(
            db=db,
            username=token_data.username,
        )

        # ? Verify user activity
        if not user.is_active or not user.is_valid:
            raise InactiveUserException()

        # ? Verify Permissions
        role = await role_crud.verify_existence(db=db, role_id=user.role.id)

        user_permission_set = {permission.code for permission in role.permissions}
        is_valid = False
        required_permission_set = set(required_permissions)
        if required_permission_set.issubset(user_permission_set):
            is_valid = True
        if not is_valid:
            raise AccessDeniedException()

        return user

    return current_user_with_permissions


# ---------------------------------------------------------------------------
def is_user_have_permission(required_permissions: list[int]) -> VerifyUserDep | None:
    async def is_user_have_permission(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme),
    ) -> VerifyUserDep:
        if not token:
            raise UserNotAuthenticatedException()
        result = VerifyUserDep()

        # ? Verify Token
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenData(username=payload["username"], role=payload["role"])

        # ? Verify User
        user = await user_crud.verify_existence_by_username(
            db=db,
            username=token_data.username,
        )

        # ? Verify user activity
        if not user.is_active or not user.is_valid:
            raise InactiveUserException()

        result.user = user

        # ? Verify Permissions
        role = await role_crud.verify_existence(db=db, role_id=user.role.id)

        user_permission_set = {permission.code for permission in role.permissions}
        required_permission_set = set(required_permissions)
        if not required_permission_set.issubset(user_permission_set):
            result.is_valid = False
            return result

        result.is_valid = True
        return result

    return is_user_have_permission


# ---------------------------------------------------------------------------
def minio_auth() -> MinioClient:
    minio_client = MinioClient(
        url=settings.MINIO_URL,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        default_bucket=settings.MINIO_DEFAULT_BUCKET,
        site_media_bucket=settings.MINIO_SITE_MEDIA_BUCKET,
        profile_image_bucket=settings.MINIO_PROFILE_IMAGE_BUCKET,
        capital_transfer_media_bucket=settings.MINIO_CAPITAL_TRANSFER_BUCKET,
        contract_media_bucket=settings.MINIO_CONTRACT_BUCKET,
        user_media_bucket=settings.MINIO_USER_IMAGE_BUCKET,
    )
    return minio_client
