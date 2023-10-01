from fastapi import APIRouter, Depends
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.auth.exception import AccessDeniedException
from src.permission import permission_codes as permission
from src.schema import IDRequest, VerifyUserDep
from src.transaction.crud import transaction as transaction_crud
from src.transaction.models import Transaction
from src.transaction.schema import TransactionFilter, TransactionRead

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/transaction", tags=["transaction"])


# ---------------------------------------------------------------------------
@router.post("/list", response_model=list[TransactionRead])
async def read_transaction_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_TRANSACTION]),
    ),
    filter_data: TransactionFilter,
    skip: int = 0,
    limit: int = 10,
) -> list[TransactionRead]:
    """
    ! Read transactions list

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
    transaction_list
        List of transaction

    """
    # * Prepare filter fields
    filter_data.gt_value = (
        (Transaction.value >= filter_data.gt_value) if filter_data.gt_value else True
    )
    filter_data.lt_value = (
        (Transaction.value <= filter_data.lt_value) if filter_data.lt_value else True
    )
    filter_data.value_type = (
        (Transaction.value_type == filter_data.value_type)
        if filter_data.value_type
        else True
    )
    filter_data.gt_created_date = (
        (Transaction.created_at >= filter_data.gt_created_date)
        if filter_data.gt_created_date
        else True
    )
    filter_data.lt_created_date = (
        (Transaction.created_at <= filter_data.lt_created_date)
        if filter_data.lt_created_date
        else True
    )

    # # * Add filter fields
    query = select(Transaction).filter(
        and_(
            or_(
                filter_data.value_type,
            ),
            and_(
                filter_data.gt_value,
                filter_data.lt_value,
            ),
            and_(
                filter_data.gt_created_date,
                filter_data.lt_created_date,
            ),
        ),
    )

    # * Have permissions
    if verify_data.is_valid:
        transaction_list = await transaction_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            query=query,
        )
    # * Verify transaction receiver & transferor
    else:
        q1 = Transaction.receiver_id == verify_data.user.wallet.id
        q2 = Transaction.transferor_id == verify_data.user.wallet.id
        query = query.where(or_(q1, q2))
        transaction_list = await transaction_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            query=query,
        )

    return transaction_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=TransactionRead)
async def find_transaction_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_PAYMENT]),
    ),
    input_data: IDRequest,
) -> TransactionRead:
    """
    ! Find Transaction by id

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    input_data
        Target Transaction's ID

    Returns
    -------
    transaction
        Found Item

    Raises
    ------
    AccessDeniedException
    TransactionNotFoundException
    """
    # ? Verify transaction existence
    transaction = await transaction_crud.verify_existence(
        db=db,
        transaction_id=input_data.id,
    )

    # * Have permissions
    if verify_data.is_valid:
        return transaction
    # * Verify transaction receiver & transferor
    else:
        is_receiver = transaction.receiver.user_id == verify_data.user.id
        is_transferor = transaction.transferor.user_id == verify_data.user.id
        if is_receiver or is_transferor:
            return transaction
        else:
            raise AccessDeniedException()
