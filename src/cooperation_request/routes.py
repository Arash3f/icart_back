from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.cooperation_request.crud import cooperation_request as cooperation_request_crud
from src.log.crud import log as log_crud
from src.location.crud import location as location_crud
from src.cooperation_request.schema import (
    CooperationRequestCreate,
    CooperationRequestRead,
    CooperationRequestUpdateStatus,
)
from src.log.models import LogType
from src.permission import permission_codes as permission
from src.schema import DeleteResponse, IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/cooperation_request", tags=["cooperation_request"])


# ---------------------------------------------------------------------------
@router.delete("/delete", response_model=DeleteResponse)
async def delete_cooperation_request(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.DELETE_COOPERATION_REQUEST]),
    ),
    delete_data: IDRequest,
) -> DeleteResponse:
    """
    ! Delete CooperationRequest

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    delete_data
        Necessary data for delete cooperation_request

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    CooperationRequestNotFoundException
    """
    # * Verify cooperation_request existence
    cooperation_request = await cooperation_request_crud.verify_existence(
        db=db,
        cooperation_request_id=delete_data.id,
    )
    # * Delete CooperationRequest
    await cooperation_request_crud.delete(db=db, item_id=delete_data.id)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.DELETE_FEE,
        detail="درخواست همکاری با {} با موفقیت توسط کاربر {} حذف شد".format(
            cooperation_request.name,
            current_user.username,
        ),
    )

    return DeleteResponse(result="CooperationRequest Deleted Successfully")


# ---------------------------------------------------------------------------
@router.post("/create", response_model=CooperationRequestRead)
async def create_cooperation_request(
    *,
    db: AsyncSession = Depends(deps.get_db),
    create_data: CooperationRequestCreate,
) -> CooperationRequestRead:
    """
    ! Create CooperationRequest

    Parameters
    ----------
    db
        Target database connection
    create_data
        Necessary data for create cooperation_request

    Returns
    -------
    cooperation_request
        New cooperation_request

    Raises
    ------
    LocationNotFoundException
    """
    await location_crud.verify_existence(
        db=db,
        location_id=create_data.location_id,
    )
    # * Create CooperationRequest
    cooperation_request = await cooperation_request_crud.create(
        db=db,
        obj_in=create_data,
    )

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.ADD_FEE,
        detail="درخواست همکاری {} با موفقیت توسط کاربر ایجاد شد".format(
            cooperation_request.name,
        ),
    )

    return cooperation_request


# ---------------------------------------------------------------------------
@router.put("/update/status", response_model=DeleteResponse)
async def update_cooperation_request(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_COOPERATION_REQUEST]),
    ),
    update_data: CooperationRequestUpdateStatus,
) -> DeleteResponse:
    """
    ! Update CooperationRequest status

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update cooperation_request

    Returns
    -------
    cooperation_request
        Updated cooperation_request

    Raises
    ------
    CooperationRequestNotFoundException
    """
    # * Verify cooperation_request existence
    req = await cooperation_request_crud.verify_existence(
        db=db,
        cooperation_request_id=update_data.where.id,
    )
    req.status = update_data.data.status
    db.add(req)
    await db.commit()

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.UPDATE_FEE,
        detail="وضعیت درخواست همکاری {} با موفقیت توسط کاربر {} ویرایش شد".format(
            req.name,
            current_user.username,
        ),
    )

    return DeleteResponse(result="CooperationRequest Updated Successfully")


# ---------------------------------------------------------------------------
@router.post("/list", response_model=list[CooperationRequestRead])
async def read_cooperation_request_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_COOPERATION_REQUEST]),
    ),
    skip: int = 0,
    limit: int = 10,
) -> list[CooperationRequestRead]:
    """
    ! Read CooperationRequest

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
    cooperation_request_list
        List of cooperation_request
    """
    cooperation_request_list = await cooperation_request_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
    )
    return cooperation_request_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=CooperationRequestRead)
async def find_cooperation_request(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_COOPERATION_REQUEST]),
    ),
    read_data: IDRequest,
) -> CooperationRequestRead:
    """
    ! Find CooperationRequest

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    read_data
        Target CooperationRequest's ID

    Returns
    -------
    cooperation_request
        Found CooperationRequest

    Raises
    ------
    CooperationRequestNotFoundException
    """
    # * Verify cooperation_request existence
    cooperation_request = await cooperation_request_crud.verify_existence(
        db=db,
        cooperation_request_id=read_data.id,
    )
    return cooperation_request
