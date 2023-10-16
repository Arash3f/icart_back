from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from src import deps
from src.merchant.crud import merchant as merchant_crud
from src.merchant.schema import MerchantRead
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/merchant", tags=["merchant"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=MerchantRead)
async def get_merchant(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    item_id: UUID,
) -> MerchantRead:
    """
    ! Find Merchant

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    item_id
        Target Merchant's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    MerchantNotFoundException
    """
    # ? Verify merchant existence
    obj = await merchant_crud.verify_existence(db=db, merchant_id=item_id)

    return obj


# ---------------------------------------------------------------------------
@router.get(path="/list", response_model=List[MerchantRead])
async def get_merchant_list(
    *,
    db=Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20,
) -> List[MerchantRead]:
    """
    ! Get All Merchant

    Parameters
    ----------
    db
        Target database connection
    skip
        Pagination skip
    limit
        Pagination limit

    Returns
    -------
    obj_list
        List of merchants
    """
    obj_list = await merchant_crud.get_multi(db=db, skip=skip, limit=limit)
    return obj_list


# ---------------------------------------------------------------------------
@router.get(path="/me", response_model=MerchantRead)
async def me(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> MerchantRead:
    """
    ! Get My Merchant Data

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User

    Returns
    -------
    obj
        Found merchant

    Raises
    ------
    MerchantNotFoundException
    """
    obj = await merchant_crud.find_by_user_id(db=db, user_id=current_user.id)
    return obj
