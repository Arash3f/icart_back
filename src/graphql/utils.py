from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.auth.exception import UserNotAuthenticatedException
from src.core.config import settings
from src.deps import get_db, TokenData


async def get_token(kwargs: dict) -> tuple[AsyncSession, str]:
    """
    ! Get Token from Graphql Info object

    Parameters
    ----------
    kwargs
        graphql object

    Returns
    -------
    db
        database object
    token
        user token

    Raises
    ------
    UserNotAuthenticatedException
    """
    db: AsyncSession = await anext(get_db())
    request: Request = kwargs["info"].context["request"]
    token = request.headers.get("Authorization", None)

    if not token:
        raise UserNotAuthenticatedException()

    return db, token


def get_user_data_from_token(token: str) -> TokenData:
    """
    ! Get User data from token

    Parameters
    ----------
    token
        user's token

    Returns
    -------
    token_data
        Token data
    """
    payload = jwt.decode(
        token=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    token_data = TokenData(username=payload["username"], role=payload["role"])

    return token_data
