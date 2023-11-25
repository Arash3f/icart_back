from sqlalchemy import select, and_

from src import deps
from src.auth.exception import AccessDeniedException
from src.band_card.models import BankCard
from src.schema import IDRequest, VerifyUserDep
from src.user.models import User
from src.wallet.exception import LackOfMoneyException
from src.deposit.crud import deposit as deposit_crud
from src.permission import permission_codes
from src.band_card.crud import bank_card as bank_card_crud
from src.deposit.models import Deposit
from src.deposit.schemas import (
    DepositCreate,
    DepositFilter,
    DepositRead,
)

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/deposit", tags=["deposit"])


# ---------------------------------------------------------------------------
@router.post("/list", response_model=list[DepositRead])
async def read_transaction_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission_codes.VIEW_WITHDRAW]),
    ),
    filter_data: DepositFilter,
    skip: int = 0,
    limit: int = 10,
) -> list[DepositRead]:
    """
    ! Read Deposit list

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    skip
        Pagination skip
    limit
        Pagination limit
    filter_data
        Filter data

    Returns
    -------
    deposit_list
        List of Deposit
    """
    # * Prepare filter fields
    filter_data.wallet_id = (
        (Deposit.wallet_id == filter_data.wallet_id)
        if filter_data.wallet_id is not None
        else True
    )
    filter_data.zibal_track_id = (
        (Deposit.zibal_track_id == filter_data.zibal_track_id)
        if filter_data.zibal_track_id is not None
        else True
    )

    # * Add filter fields
    query = (
        select(Deposit)
        .filter(
            and_(
                filter_data.wallet_id,
                filter_data.zibal_track_id,
            ),
        )
        .order_by(Deposit.created_at.desc())
    )

    # * Have permissions
    if verify_data.is_valid:
        deposit_list = await deposit_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            query=query,
        )
    # * Verify transaction receiver & transferor
    else:
        query = query.where(
            BankCard.user_id == verify_data.user.id,
        )
        deposit_list = await deposit_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            query=query,
        )

    return deposit_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=DepositRead)
async def find_transaction_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission_codes.VIEW_WITHDRAW]),
    ),
    input_data: IDRequest,
) -> DepositRead:
    """
    ! Find Deposit by id

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    input_data
        Target Deposit ID

    Returns
    -------
    deposit
        Found Item

    Raises
    ------
    DepositNotFound
    AccessDeniedException
    """
    # ? Verify transaction existence
    deposit = await deposit_crud.verify_existence(
        db=db,
        deposit_id=input_data.id,
    )

    # * Have permissions
    if verify_data.is_valid:
        return deposit
    # * Verify transaction receiver & transferor
    else:
        if deposit.wallet_id == verify_data.user.wallet.id:
            return deposit
        else:
            raise AccessDeniedException()
