from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from src.core.config import settings

# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """
    ! Hashing password

    Parameters
    ----------
    password
        Target password

    Returns
    -------
    hash_password
        hashed password
    """
    hash_password = pwd_context.hash(password)
    return hash_password


# ---------------------------------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    ! Verify password with hash password

    Parameters
    ----------
    plain_password
        The password to be confirmed
    hashed_password
        The hashed password

    Returns
    -------
    res
        Result of operation
    """
    result = pwd_context.verify(plain_password, hashed_password)
    return result


# ---------------------------------------------------------------------------
def generate_access_token(
    data: dict[str, Any],
    expire_delta: timedelta | None = None,
) -> str:
    """
    ! Generate access token

    Parameters
    ----------
    data
        Token input data
    expire_delta
        Token expire time

    Returns
    -------
    encoded_data
        Jwt Token
    """
    data_to_encode = data.copy()
    if expire_delta:
        expire_time = datetime.utcnow() + expire_delta
    else:
        expire_time = datetime.utcnow() + timedelta(hours=1)

    data_to_encode.update({"exp": expire_time})
    encoded_data = jwt.encode(
        claims=data_to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_data
