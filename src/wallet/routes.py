from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.permission import permission_codes as permission
from src.schema import IDRequest
from src.user.models import User
from src.wallet.crud import wallet as wallet_crud
from src.agent.crud import agent as agent_crud
from src.credit.crud import credit as credit_crud
from src.transaction.crud import transaction as transaction_crud
from src.merchant.crud import merchant as merchant_crud
from src.organization.crud import organization as organization_crud
from src.wallet.models import Wallet
from src.wallet.schema import (
    WalletRead,
    WalletAdditionalInfo,
    WalletBalanceRead,
    WalletFilter,
    WalletFilterOrderFild,
)

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
    WalletNotFoundException
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
    filter_data: WalletFilter,
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
    # * Prepare filter fields
    filter_data.number = (
        (Wallet.number.contains(filter_data.number))
        if filter_data.number is not None
        else True
    )
    filter_data.is_lock = (
        (Wallet.is_lock == filter_data.is_lock)
        if filter_data.is_lock is not None
        else True
    )
    filter_data.name = (
        or_(
            User.first_name.contains(filter_data.name),
            User.last_name.contains(filter_data.name),
        )
        if filter_data.name is not None
        else True
    )
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code is not None
        else True
    )
    # * Add filter fields
    query = (
        select(Wallet)
        .filter(
            and_(
                filter_data.number,
                filter_data.name,
                filter_data.is_lock,
                filter_data.national_code,
            ),
        )
        .join(Wallet.user)
        .order_by(Wallet.created_at.desc())
    )

    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == WalletFilterOrderFild.number:
                query = query.order_by(Wallet.number.desc())
            elif field == WalletFilterOrderFild.is_lock:
                query = query.order_by(Wallet.is_lock.desc())
            elif field == WalletFilterOrderFild.created_at:
                query = query.order_by(Wallet.created_at.desc())
            elif field == WalletFilterOrderFild.updated_at:
                query = query.order_by(Wallet.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == WalletFilterOrderFild.number:
                query = query.order_by(Wallet.number.asc())
            elif field == WalletFilterOrderFild.is_lock:
                query = query.order_by(Wallet.is_lock.asc())
            elif field == WalletFilterOrderFild.created_at:
                query = query.order_by(Wallet.created_at.asc())
            elif field == WalletFilterOrderFild.updated_at:
                query = query.order_by(Wallet.updated_at.asc())

    wallet_list = await wallet_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
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

    Raises
    ------
    WalletNotFoundException
    """
    # * Verify wallet existence
    wallet = await wallet_crud.verify_by_user_id(db=db, user_id=current_user.id)
    return wallet


# ---------------------------------------------------------------------------
@router.get(path="/my/balance", response_model=WalletBalanceRead)
async def get_my_wallet_balance(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> WalletBalanceRead:
    """
    ! Get My Wallet balance

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User

    Returns
    -------
    wallet
        my wallet balance
    """
    return WalletBalanceRead(
        cash_balance=current_user.cash.balance,
        credit_balance=current_user.credit.balance,
    )


# ---------------------------------------------------------------------------
@router.get("/additional_info", response_model=WalletAdditionalInfo)
async def get_organization_additional_info(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> WalletAdditionalInfo:
    organization_users = 0
    merchant_count = 0

    transaction_count = await transaction_crud.get_transaction_count(
        db=db,
        wallet_id=current_user.wallet.id,
    )
    income = await transaction_crud.get_income(
        db=db,
        wallet_id=current_user.wallet.id,
    )
    credit = await credit_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )
    if current_user.role.name == "سازمان":
        organization_users = await organization_crud.get_organization_users_count(
            db=db,
            user_id=current_user.id,
        )
    if current_user.role.name == "نماینده":
        agent = await agent_crud.find_by_user_id(db=db, user_id=current_user.id)
        merchant_count = await merchant_crud.get_merchant_users_count_by_agent_id(
            db=db,
            agent_id=agent.id,
        )

    return WalletAdditionalInfo(
        income=income,
        transaction_count=transaction_count,
        organization_users=organization_users,
        used_credit=credit.used,
        received_credit=credit.received,
        paid_credit=credit.paid,
        merchant_count=merchant_count,
        credit_consumed=credit.consumed,
        debt_to_acceptor=credit.debt,
        settled_amount=0,
        credit_amount=credit.balance,
        organizations_count=organization_users,
        unsettled_credit=0,
    )
