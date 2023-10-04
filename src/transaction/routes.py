from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import and_, or_, select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.auth.exception import AccessDeniedException
from src.permission import permission_codes as permission
from src.schema import (
    IDRequest,
    VerifyUserDep,
    Duration,
    ChartResponse,
    ChartFilterInput,
)
from src.transaction.crud import transaction as transaction_crud
from src.transaction.models import Transaction, TransactionValueType
from src.transaction.schema import (
    TransactionFilter,
    TransactionRead,
    TransactionAggregateResponse,
    TransactionChartFilter,
    TransactionChartType,
)
from src.user.models import User

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
        query = query.where(or_(q1, q2)).order_by(desc(Transaction.created_at))
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


# ---------------------------------------------------------------------------
@router.post("/transaction/count", response_model=list[ChartResponse])
async def get_transaction_count(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    filter_data: ChartFilterInput,
) -> list[ChartResponse]:
    """
    ! Get transaction's count for chart

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user
    filter_data
        filter data

    Returns
    -------
    chart_data
        chart final data
    """
    start = filter_data.duration.start_date
    end = filter_data.duration.end_date
    unit = filter_data.unit

    chart_data: list[ChartResponse] = []

    # ? calculate durations
    buf_time = start
    while buf_time < end:
        buf_end = buf_time + timedelta(
            days=unit,
        )
        duration = Duration(
            start_date=buf_time,
            end_date=buf_end,
        )
        obj = ChartResponse(
            duration=duration,
            value=0,
        )

        query = (
            select(func.count())
            .select_from(Transaction)
            .filter(
                and_(
                    or_(
                        Transaction.transferor_id == current_user.wallet.id,
                        Transaction.receiver_id == current_user.wallet.id,
                    ),
                    Transaction.created_at >= obj.duration.start_date,
                    Transaction.created_at < obj.duration.end_date,
                ),
            )
        )
        response = await db.execute(
            query,
        )
        obj.value = response.scalar()

        chart_data.append(obj)
        buf_time = buf_end

    return chart_data


# ---------------------------------------------------------------------------
@router.post("/transaction/income_and_expense", response_model=list[ChartResponse])
async def get_transaction_income_and_expense(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    filter_data: TransactionChartFilter,
) -> list[ChartResponse]:
    """
    ! Get wallet income or expense

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user
    filter_data
        filter data

    Returns
    -------
    chart_data
        chart final data
    """
    start = filter_data.duration.start_date
    end = filter_data.duration.end_date
    unit = filter_data.unit

    if filter_data.type == TransactionChartType.INCOME:
        query_filter = Transaction.receiver_id == current_user.wallet.id
    else:
        query_filter = Transaction.transferor_id == current_user.wallet.id

    chart_data: list[ChartResponse] = []

    # ? calculate durations
    buf_time = start
    while buf_time < end:
        buf_end = buf_time + timedelta(
            days=unit,
        )
        duration = Duration(
            start_date=buf_time,
            end_date=buf_end,
        )
        obj = ChartResponse(
            duration=duration,
            value=0,
        )

        query = (
            select(func.sum(Transaction.value))
            .select_from(Transaction)
            .filter(
                and_(
                    query_filter,
                    Transaction.created_at >= obj.duration.start_date,
                    Transaction.created_at < obj.duration.end_date,
                ),
            )
        )
        response = await db.execute(
            query,
        )
        obj.value = response.scalar()

        chart_data.append(obj)
        buf_time = buf_end

    return chart_data


# ---------------------------------------------------------------------------
@router.post("/transaction/aggregate", response_model=TransactionAggregateResponse)
async def get_transaction_aggregate(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> TransactionAggregateResponse:
    """
    ! Get wallet aggregate of transaction type

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user

    Returns
    -------

    """
    result = TransactionAggregateResponse(
        cache=0,
        credit=0,
    )

    query = (
        select(Transaction.value_type, func.sum(Transaction.value))
        .select_from(Transaction)
        .filter(
            Transaction.receiver_id == current_user.wallet.id,
        )
        .group_by(Transaction.value_type)
    )
    response = await db.execute(query)
    response = response.all()

    for data in response:
        if data[0] == TransactionValueType.CASH:
            result.cache = int(data[1])
        elif data[0] == TransactionValueType.CREDIT:
            result.credit = int(data[1])

    return result
