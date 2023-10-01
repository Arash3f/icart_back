from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select

from src import deps
from src.capital_transfer.crud import capital_transfer as capital_transfer_crud
from src.capital_transfer.models import CapitalTransfer, CapitalTransferEnum
from src.capital_transfer.schema import (
    CapitalTransferCreate,
    CapitalTransferInDB,
    CapitalTransferRead,
)
from src.schema import IDRequest
from src.user.models import User
from src.wallet.crud import wallet as wallet_crud

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/capital_transfer", tags=["capital_transfer"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=CapitalTransferRead)
async def find_capital_transfer(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    obj_data: IDRequest,
) -> CapitalTransferRead:
    """
    ! Get one CapitalTransfer

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target CapitalTransfer's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    CapitalTransferNotFoundException
    """
    obj = await capital_transfer_crud.verify_existence(
        db=db,
        capital_transfer_id=obj_data.id,
    )

    return obj


# ---------------------------------------------------------------------------
@router.get(path="/list", response_model=List[CapitalTransferRead])
async def get_capital_transfer(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    skip: int = 0,
    limit: int = 20,
) -> List[CapitalTransferRead]:
    """
    ! Get All CapitalTransfer

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
        List of capital transfer

    """
    obj_list = await capital_transfer_crud.get_multi(db=db, skip=skip, limit=limit)
    return obj_list


# ---------------------------------------------------------------------------
@router.get(path="/list/my", response_model=List[CapitalTransferRead])
async def get_capital_transfer_list_my(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    skip: int = 0,
    limit: int = 20,
) -> List[CapitalTransferRead]:
    """
    ! Get All My CapitalTransfer

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
        List of my capital transfer

    """
    wallet = await wallet_crud.get_main_wallet_with_user_id(
        db=db,
        user_id=current_user.id,
    )
    query = select(CapitalTransfer).where(CapitalTransfer.receiver_id == wallet.id)
    obj_list = await capital_transfer_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list


# ---------------------------------------------------------------------------
@router.post(path="/create", response_model=CapitalTransferRead)
async def create_capital_transfer(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    create_data: CapitalTransferCreate,
) -> CapitalTransferRead:
    """
    ! Create CapitalTransfer with permission
    # todo: add Image

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    create_data
        Necessary data for create capital transfer

    Returns
    -------
    capital_transfer
        New position_request

    Raises
    ------
    WalletNotFoundException
        It does not happen normally
    """
    wallet = await wallet_crud.get_main_wallet_with_user_id(
        db=db,
        user_id=current_user.id,
    )
    data = CapitalTransferInDB(**create_data.model_dump(), receiver_id=wallet.id)
    capital_transfer = await capital_transfer_crud.create(db=db, obj_in=data)

    return capital_transfer


# ---------------------------------------------------------------------------
@router.put(path="/approve", response_model=CapitalTransferRead)
async def update_position_request(
    *,
    db=Depends(deps.get_db),
    obj_data: IDRequest,
    current_user: User = Depends(deps.get_current_user()),
) -> CapitalTransferRead:
    """
    ! Approve CapitalTransfer

    Parameters
    ----------
    db
        Target database connection
    obj_data
        Capital transfer item
    current_user
        Requester User

    Returns
    -------
    obj_current
        Updated capital transfer

    Raises
    ------
    CapitalTransferNotFoundException
    """
    # ? Verify capital_transfer existence
    obj_current = await capital_transfer_crud.verify_existence(
        db=db,
        capital_transfer_id=obj_data.id,
    )

    obj_current.finish = True
    wallet = await wallet_crud.get(db=db, item_id=obj_current.receiver_id)
    # Todo: Create Transaction
    if obj_current.transfer_type == CapitalTransferEnum.Credit:
        wallet.credit_balance += obj_current.value
    elif obj_current.transfer_type == CapitalTransferEnum.Cash:
        wallet.cash_balance += obj_current.value

    db.add(obj_current)
    await db.commit()
    await db.refresh(obj_current)
    return obj_current
