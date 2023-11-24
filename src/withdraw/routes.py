from sqlalchemy import select, and_

from src import deps
from src.auth.exception import AccessDeniedException
from src.band_card.models import BankCard
from src.schema import IDRequest, VerifyUserDep
from src.user.models import User
from src.wallet.exception import LackOfMoneyException
from src.withdraw.crud import withdraw as withdraw_crud
from src.permission import permission_codes
from src.band_card.crud import bank_card as bank_card_crud
from src.withdraw.models import Withdraw
from src.withdraw.schemas import (
    WithdrawCreate,
    WithdrawReadWithBankInfo,
    ValidateInput,
    WithdrawFilter,
)

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/withdraw", tags=["withdraw"])


# ---------------------------------------------------------------------------
@router.post("/list", response_model=list[WithdrawReadWithBankInfo])
async def read_transaction_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission_codes.VIEW_WITHDRAW]),
    ),
    filter_data: WithdrawFilter,
    skip: int = 0,
    limit: int = 10,
) -> list[WithdrawReadWithBankInfo]:
    """
    ! Read Withdraw list

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
    withdraw_list
        List of Withdraw
    """
    # * Prepare filter fields
    filter_data.is_done = (
        (Withdraw.is_done == filter_data.is_done)
        if filter_data.is_done is not None
        else True
    )
    filter_data.is_verified = (
        (Withdraw.is_done == filter_data.is_verified)
        if filter_data.is_verified is not None
        else True
    )

    # * Add filter fields
    query = (
        select(Withdraw)
        .filter(
            and_(
                filter_data.is_done,
                filter_data.is_verified,
            ),
        )
        .order_by(Withdraw.created_at.desc())
    ).join(Withdraw.bank_card)

    # * Have permissions
    if verify_data.is_valid:
        withdraw_list = await withdraw_crud.get_multi(
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
        withdraw_list = await withdraw_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            query=query,
        )

    return withdraw_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=WithdrawReadWithBankInfo)
async def find_transaction_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission_codes.VIEW_WITHDRAW]),
    ),
    input_data: IDRequest,
) -> WithdrawReadWithBankInfo:
    """
    ! Find Withdraw by id

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    input_data
        Target Withdraw ID

    Returns
    -------
    withdraw
        Found Item

    Raises
    ------
    WithdrawNotFound
    AccessDeniedException
    """
    # ? Verify transaction existence
    withdraw = await withdraw_crud.verify_existence(
        db=db,
        withdraw_id=input_data.id,
    )

    # * Have permissions
    if verify_data.is_valid:
        return withdraw
    # * Verify transaction receiver & transferor
    else:
        bank_card = await bank_card_crud.find_by_id_and_user_id(
            db=db,
            bank_card_id=withdraw.bank_card_id,
            user_id=verify_data.user.id,
        )
        if bank_card:
            return withdraw
        else:
            raise AccessDeniedException()


# ---------------------------------------------------------------------------
@router.post("/create", response_model=WithdrawReadWithBankInfo)
async def create_withdraw_request(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    withdraw_in: WithdrawCreate,
):
    await bank_card_crud.verify_existence_by_id_and_user_id(
        db=db,
        bank_card_id=withdraw_in.bank_card_id,
        user_id=current_user.id,
    )
    if withdraw_in.amount > current_user.cash.balance:
        raise LackOfMoneyException()
    created_withdraw = await withdraw_crud.create(db=db, obj_in=withdraw_in)
    return created_withdraw


# ---------------------------------------------------------------------------
@router.put("/validate", response_model=WithdrawReadWithBankInfo)
async def accept_or_deny_withdraw(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission_codes.VALIDATE_WITHDRAW]),
    ),
    validate_data: ValidateInput,
):
    withdraw = await withdraw_crud.verify_existence(
        db=db,
        withdraw_id=validate_data.where.id,
    )
    update_schema = {"is_verified": validate_data.data.is_valid}
    updated_withdraw = await withdraw_crud.update(
        db=db,
        obj_current=withdraw,
        obj_new=update_schema,
    )
    return updated_withdraw
