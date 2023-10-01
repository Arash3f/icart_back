from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select

from src import deps
from src.permission import permission_codes as permission
from src.schema import IDRequest
from src.user.models import User
from src.user_crypto.crud import user_crypto as user_crypto_crud
from src.user_crypto.models import UserCrypto
from src.user_crypto.schema import UserCryptoRead
from src.wallet.crud import wallet as wallet_crud

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/user_crypto", tags=["user_crypto"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=UserCryptoRead)
async def get_user_crypto(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_USER_CRYPTO]),
    ),
    obj_data: IDRequest,
) -> UserCryptoRead:
    """
    ! Find UserCrypto

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target UserCrypto's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    UserCryptoNotFoundException
    """
    # * Verify user_crypto existence
    obj = await user_crypto_crud.verify_existence(db=db, user_crypto_id=obj_data.id)
    return obj


# ---------------------------------------------------------------------------
@router.get(path="/list", response_model=List[UserCryptoRead])
async def get_user_crypto_list(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_USER_CRYPTO]),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[UserCryptoRead]:
    """
    ! Get All UserCrypto

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    skip
        Pagination skip
    limit
        Pagination limit

    Returns
    -------
    obj_list
        list of user crypto
    """
    obj_list = await user_crypto_crud.get_multi(db=db, skip=skip, limit=limit)
    return obj_list


# ---------------------------------------------------------------------------
@router.get(path="/my", response_model=List[UserCryptoRead])
async def get_user_crypto_list_my(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    skip: int = 0,
    limit: int = 20,
) -> List[UserCryptoRead]:
    """
    ! Get My UserCrypto

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    skip
        Pagination skip
    limit
        Pagination limit

    Returns
    -------
    obj_list
        list of my user crypto

    Raises
    ------
    WalletNotFoundException
    """
    wallet = await wallet_crud.find_by_user_id(db=db, user_id=current_user.id)
    query = select(UserCrypto).where(UserCrypto.wallet_id == wallet.id)
    obj_list = await user_crypto_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list
