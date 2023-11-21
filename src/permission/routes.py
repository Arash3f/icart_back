from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.permission import permission_codes as permission
from src.permission.crud import permission as permission_crud
from src.permission.models import Permission
from src.permission.schema import (
    PermissionRead,
    PermissionFilter,
    PermissionFilterOrderFild,
)
from src.schema import IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/permission", tags=["permission"])


# ---------------------------------------------------------------------------
@router.get("/list", response_model=list[PermissionRead])
async def read_permissions_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_PERMISSION]),
    ),
    filter_data: PermissionFilter,
    skip: int = 0,
    limit: int = 20,
):
    """
    ! Get All Permissions

    Parameters
    ----------
    db
        Target database connection
    current_user
        Required permissions
    skip
        Pagination skip
    limit
        Pagination limit
    filter_data
        Filter data

    Returns
    -------
    permission_list
        List of permissions
    """
    # * Prepare filter fields
    filter_data.name = (
        Permission.name.contains(filter_data.name)
        if filter_data.name is not None
        else True
    )
    # * Add filter fields
    query = (
        select(Permission)
        .filter(
            filter_data.name,
        )
        .order_by(Permission.created_at.desc())
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == PermissionFilterOrderFild.name:
                query = query.order_by(Permission.name.desc())
            elif field == PermissionFilterOrderFild.created_at:
                query = query.order_by(Permission.created_at.desc())
            elif field == PermissionFilterOrderFild.updated_at:
                query = query.order_by(Permission.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == PermissionFilterOrderFild.name:
                query = query.order_by(Permission.name.asc())
            elif field == PermissionFilterOrderFild.created_at:
                query = query.order_by(Permission.created_at.asc())
            elif field == PermissionFilterOrderFild.updated_at:
                query = query.order_by(Permission.updated_at.asc())
    # * Find All agent with filters
    permission_list = await permission_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return permission_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=PermissionRead)
async def read_permission(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_PERMISSION]),
    ),
    obj_data: IDRequest,
):
    """
    ! Find Permission

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target Location's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    PermissionNotFoundException
    """
    # * Verify location existence
    obj = await permission_crud.verify_existence(db=db, permission_id=obj_data.id)
    return obj
