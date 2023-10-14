from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.permission import permission_codes as permission
from src.schema import IDRequest
from src.user.models import User
from src.wallet.crud import wallet as wallet_crud
from src.agent.crud import agent as agent_crud
from src.transaction.crud import transaction as transaction_crud
from src.merchant.crud import merchant as merchant_crud
from src.organization.crud import organization as organization_crud
from src.wallet.schema import WalletRead, WalletAdditionalInfo, WalletBalanceRead

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


# ---------------------------------------------------------------------------
@router.get(path="/my/balance", response_model=WalletBalanceRead)
async def get_my_wallet(
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
    transaction_count = await transaction_crud.get_transaction_count(
        db=db,
        wallet_id=current_user.wallet.id,
    )

    income = await transaction_crud.get_income(
        db=db,
        wallet_id=current_user.wallet.id,
    )
    organization_users = 0
    if current_user.role.name == "سازمان":
        organization_users = await organization_crud.get_organization_users_count(
            db=db,
            user_id=current_user.id,
        )

    merchant_count = 0
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
        used_credit=0,
        received_credit=int(current_user.credit.received),
        paid_credit=int(current_user.credit.paid),
        merchant_count=merchant_count,
        credit_consumed=0,
        debt_to_acceptor=0,
        settled_amount=0,
        credit_amount=0,
        organizations_count=organization_users,
        unsettled_credit=0,
    )
