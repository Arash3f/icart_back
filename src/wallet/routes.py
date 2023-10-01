from typing import List

from fastapi import APIRouter, Depends

from src import deps
from src.permission import permission_codes as permission
from src.schema import IDRequest
from src.user.models import User
from src.wallet.crud import wallet as wallet_crud
from src.wallet.schema import WalletRead

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/wallet", tags=["wallet"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=WalletRead)
async def get_wallet(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_WALLET]),
    ),
    read_data: IDRequest,
) -> WalletRead:
    """
    ! Find Wallet

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    read_data
        Target Wallet's ID

    Returns
    -------
    wallet
        Found Item

    Raises
    ------


    """
    # * Verify wallet existence
    wallet = await wallet_crud.verify_existence(db=db, wallet_id=read_data.id)
    return wallet


# ---------------------------------------------------------------------------
@router.get(path="/list", response_model=List[WalletRead])
async def get_wallet_list(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_WALLET]),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[WalletRead]:
    """
    ! Get All Wallet

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
    wallet_list
        all system wallets
    """
    wallet_list = await wallet_crud.get_multi(db=db, skip=skip, limit=limit)
    return wallet_list


# ---------------------------------------------------------------------------
@router.get(path="/my", response_model=WalletRead)
async def get_my_wallet(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> WalletRead:
    """
    ! Get My Wallet

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User

    Returns
    -------
    wallet
        my wallet
    """
    # * Verify wallet existence
    wallet = await wallet_crud.verify_by_user_id(db=db, user_id=current_user.id)
    return wallet
