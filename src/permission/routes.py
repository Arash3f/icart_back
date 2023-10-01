from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.permission import permission_codes as permission
from src.permission.crud import permission as permission_crud
from src.permission.schema import PermissionRead
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

    Returns
    -------
    permission_list
        List of permissions

    """
    permission_list = await permission_crud.get_multi(db=db, skip=skip, limit=limit)
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
