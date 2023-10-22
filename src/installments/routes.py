from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_

from src import deps
from src.installments.crud import installments as installments_crud
from src.installments.models import Installments
from src.installments.schema import (
    InstallmentsCreate,
    InstallmentsFilter,
    InstallmentsRead,
    InstallmentsFilterOrderFild,
)
from src.permission import permission_codes as permission
from src.schema import IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/installments", tags=["installments"])


# ---------------------------------------------------------------------------
@router.post(path="/pay", response_model=InstallmentsRead)
async def create_installments(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CREATE_LOCATION]),
    ),
    create_data: InstallmentsCreate,
) -> InstallmentsRead:
    """
    ! Create Installments

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    create_data
        Necessary data for create installments

    Returns
    -------
    obj
        New installments

    Raises
    ------
    InstallmentsNameIsDuplicatedException
    InstallmentsParentNotFoundException
    InstallmentsNotFoundException
    """
    # * Verify parent existence
    if create_data.parent_id:
        await installments_crud.verify_existence(
            db=db,
            installments_id=create_data.parent_id,
            parent_exception=True,
        )
    # * Verify installments name duplicate
    await installments_crud.verify_duplicate_name(db=db, name=create_data.name)

    obj = await installments_crud.create(db=db, obj_in=create_data)
    return obj


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=InstallmentsRead)
async def find_installments(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_INSTALLMENTS]),
    ),
    obj_data: IDRequest,
) -> InstallmentsRead:
    """
    ! Find Installments

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target Installments's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    InstallmentsNotFoundException
    """
    # * Verify installments existence
    obj = await installments_crud.verify_existence(db=db, installments_id=obj_data.id)

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[InstallmentsRead])
async def get_installments(
    *,
    db=Depends(deps.get_db),
    filter_data: InstallmentsFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[InstallmentsRead]:
    """
    ! Get All Installments

    Parameters
    ----------
    db
        Target database connection
    skip
        Pagination skip
    limit
        Pagination limit
    filter_data
        Filter data

    Returns
    -------
    obj_list
        List of ability
    """
    # * Prepare filter fields
    filter_data.user_id = (
        (Installments.user_id == filter_data.user_id) if filter_data.user_id else True
    )

    # * Add filter fields
    query = select(Installments).filter(
        and_(
            filter_data.user_id,
        ),
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == InstallmentsFilterOrderFild.due_date:
                query = query.order_by(Installments.due_date.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == InstallmentsFilterOrderFild.due_date:
                query = query.order_by(Installments.due_date.asc())
    # * Find All agent with filters
    obj_list = await installments_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )

    return obj_list
