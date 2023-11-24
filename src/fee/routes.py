from fastapi import APIRouter, Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.exception import InCorrectDataException
from src.fee.crud import fee as fee_crud
from src.fee.models import Fee
from src.log.crud import log as log_crud
from src.fee.schema import FeeBase, FeeCreate, FeeRead, FeeUpdate, FeeFilter
from src.log.models import LogType
from src.permission import permission_codes as permission
from src.schema import DeleteResponse, IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/fee", tags=["fee"])


# ---------------------------------------------------------------------------
@router.delete("/delete", response_model=DeleteResponse)
async def delete_fee(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.DELETE_FEE]),
    ),
    delete_data: IDRequest,
) -> DeleteResponse:
    """
    ! Delete Fee

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    delete_data
        Necessary data for delete fee

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    FeeNotFoundException
    """
    # * Verify fee existence
    fee = await fee_crud.verify_existence(db=db, fee_id=delete_data.id)
    # * Delete Fee
    await fee_crud.delete(db=db, item_id=delete_data.id)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.DELETE_FEE,
        detail="کارمزد سقف {} برای نوع {} و کاربران {}با موفقیت توسط کاربر {} حذف شد".format(
            fee.limit,
            fee.type,
            fee.user_type,
            current_user.username,
        ),
    )

    return DeleteResponse(result="Fee Deleted Successfully")


# ---------------------------------------------------------------------------
@router.post("/create", response_model=FeeBase)
async def create_fee(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CREATE_FEE]),
    ),
    create_data: FeeCreate,
) -> FeeBase:
    """
    ! Create Fee

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    create_data
        Necessary data for create fee

    Returns
    -------
    fee
        New fee

    Raises
    ------
    InCorrectDataException
    FeeLimitIsDuplicatedException
    """
    # ! Cannot set percentage & value together
    if create_data.value is not None and create_data.percentage is not None:
        raise InCorrectDataException()

    is_percentage = False
    if create_data.value is None:
        is_percentage = True

    # * Verify fee's limit duplicate
    await fee_crud.verify_duplicate_limit(
        db=db,
        limit=create_data.limit,
        user_type=create_data.user_type,
        value_type=create_data.type,
        is_percentage=is_percentage,
    )
    # * Create Fee
    fee = await fee_crud.create(db=db, obj_in=create_data)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.ADD_FEE,
        detail="کارمزد سقف {} با موفقیت توسط کاربر {} ایجاد شد".format(
            fee.limit,
            current_user.username,
        ),
    )

    return fee


# ---------------------------------------------------------------------------
@router.put("/update", response_model=FeeRead)
async def update_fee(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_FEE]),
    ),
    update_data: FeeUpdate,
) -> FeeRead:
    """
    ! Update Fee

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update fee

    Returns
    -------
    fee
        Updated fee

    Raises
    ------
    FeeNotFoundException
    FeeIsDuplicatedException
    """
    # ! Cannot set percentage & value together
    if update_data.data.value is not None and update_data.data.percentage is not None:
        raise InCorrectDataException()
    # * Verify fee existence
    obj_current = await fee_crud.verify_existence(
        db=db,
        fee_id=update_data.where.id,
    )

    is_percentage = False
    if update_data.data.value is None:
        is_percentage = True

    exception_is_percentage = False
    if obj_current.value is None:
        exception_is_percentage = True

    # * Verify fee's limit duplicate
    await fee_crud.verify_duplicate_limit(
        db=db,
        limit=update_data.data.limit,
        user_type=update_data.data.user_type,
        value_type=update_data.data.type,
        is_percentage=is_percentage,
        exception_user_type=obj_current.user_type,
        exception_value_type=obj_current.type,
        exception_is_percentage=exception_is_percentage,
        exception_limit=obj_current.limit,
    )
    # * Update fee
    fee = await fee_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.UPDATE_FEE,
        detail="کارمزد سقف {} با موفقیت توسط کاربر {} ویرایش شد".format(
            fee.limit,
            current_user.username,
        ),
    )

    return fee


# ---------------------------------------------------------------------------
@router.post("/list", response_model=list[FeeRead])
async def read_fee_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_FEE]),
    ),
    filter_data: FeeFilter,
    skip: int = 0,
    limit: int = 10,
) -> list[FeeRead]:
    """
    ! Read Fee

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
    filter_data
        Filter data

    Returns
    -------
    fee_list
        List of fee
    """
    # * Prepare filter fields
    filter_data.user_type = (
        (Fee.user_type == filter_data.user_type)
        if filter_data.user_type is not None
        else True
    )
    filter_data.type = (
        (Fee.type == filter_data.type) if filter_data.type is not None else True
    )
    # * Add filter fields
    query = (
        select(Fee).filter(
            and_(
                filter_data.user_type,
                filter_data.type,
            ),
        )
    ).order_by(Fee.created_at.desc())
    # * Find All agent with filters
    fee_list = await fee_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query.distinct(),
    )
    return fee_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=FeeRead)
async def find_fee(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_FEE]),
    ),
    read_data: IDRequest,
) -> FeeRead:
    """
    ! Find Fee

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    read_data
        Target Fee's ID

    Returns
    -------
    fee
        Found Fee

    Raises
    ------
    FeeNotFoundException
    """
    # * Verify fee existence
    fee = await fee_crud.verify_existence(db=db, fee_id=read_data.id)
    return fee
