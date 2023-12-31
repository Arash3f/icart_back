from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.exception import InCorrectDataException
from src.fee.crud import fee as fee_crud
from src.fee.schema import FeeBase, FeeCreate, FeeRead, FeeUpdate
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
    await fee_crud.verify_existence(db=db, user_crypto_id=delete_data.id)
    # * Delete Fee
    await fee_crud.delete(db=db, id=delete_data.id)

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
    if create_data.value and create_data.percentage:
        raise InCorrectDataException()

    # * Verify fee's limit duplicate
    await fee_crud.verify_duplicate_limit(db=db, limit=create_data.limit)
    # * Create Fee
    fee = await fee_crud.create(db=db, obj_in=create_data)

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
    FeeLimitIsDuplicatedException
    """
    # * Verify fee existence
    obj_current = await fee_crud.verify_existence(
        db=db,
        user_crypto_id=update_data.where.id,
    )
    # * Verify fee's limit duplicate
    await fee_crud.verify_duplicate_limit(
        db=db,
        limit=update_data.data.limit,
        exception_limit=obj_current.limit,
    )
    # * Update fee
    fee = await fee_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )

    return fee


# ---------------------------------------------------------------------------
@router.get("/list", response_model=list[FeeRead])
async def read_fee_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_FEE]),
    ),
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

    Returns
    -------
    fee_list
        List of fee
    """
    fee_list = await fee_crud.get_multi(db=db, skip=skip, limit=limit)
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
    fee = await fee_crud.verify_existence(db=db, user_crypto_id=read_data.id)
    return fee
