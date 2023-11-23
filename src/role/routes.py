from fastapi import APIRouter, Depends, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.log.models import LogType
from src.permission import permission_codes as permission
from src.permission.crud import permission as permission_crud
from src.role.crud import role as role_crud
from src.log.crud import log as log_crud
from src.role.crud import role_permission as role_permission_crud
from src.role.exception import RoleNotFoundException
from src.role.models import Role
from src.role.schema import (
    PermissionsToRole,
    RoleCreate,
    RoleFilter,
    RoleFilterOrderFild,
    RolePermissionCreate,
    RoleRead,
    RoleUpdate,
    RoleReadV2,
)
from src.schema import DeleteResponse, IDRequest, ResultResponse
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/role", tags=["role"])


# ---------------------------------------------------------------------------
@router.delete("/delete", response_model=DeleteResponse)
async def delete_role(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.DELETE_ROLE]),
    ),
    delete_data: IDRequest,
) -> DeleteResponse:
    """
    ! Delete Role

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    delete_data
        Necessary data for delete role

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    RoleNotFoundException
    RoleHaveUserException
    """
    # * Verify role existence
    obj_current = await role_crud.verify_existence(db=db, role_id=delete_data.id)

    if (
        obj_current.name == "ادمین"
        or obj_current.name == "نماینده"
        or obj_current.name == "پذیرنده"
        or obj_current.name == "سازمان"
        or obj_current.name == "کاربر ساده"
    ):
        raise RoleNotFoundException()

    # * Verify Role connections
    await role_crud.verify_connections(db=db, role_id=delete_data.id)
    # * Delete Role
    await role_crud.delete(db=db, item_id=delete_data.id)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.DELETE_ROLE,
        detail="نقش {} با موفقیت توسط کاربر {} حذف شد".format(
            obj_current.name,
            current_user.national_code,
        ),
    )

    return DeleteResponse(result="Role Deleted Successfully")


# ---------------------------------------------------------------------------
@router.post("/create", response_model=RoleRead)
async def create_role(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CREATE_ROLE]),
    ),
    create_data: RoleCreate,
) -> RoleRead:
    """
    ! Create Role

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    create_data
        Necessary data for create role

    Returns
    -------
    role
        New role

    Raises
    ------
    RoleNameIsDuplicatedException
    """
    # * Verify role's name duplicate
    await role_crud.verify_duplicate_name(db=db, name=create_data.name)
    # * Create Role
    role = await role_crud.create(db=db, obj_in=create_data)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.CREATE_ABILITY,
        detail="نقش {} با موفقیت توسط کاربر {} ایجاد شد".format(
            role.name,
            current_user.national_code,
        ),
    )

    return role


# ---------------------------------------------------------------------------
@router.put("/update", response_model=RoleRead)
async def update_role(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_ROLE]),
    ),
    update_data: RoleUpdate,
) -> RoleRead:
    """
    ! Update Role

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update role

    Returns
    -------
    role
        Updated role

    Raises
    ------
    RoleNotFoundException
    RoleNameIsDuplicatedException
    """
    # * Verify role existence
    obj_current = await role_crud.verify_existence(db=db, role_id=update_data.where.id)
    if (
        obj_current.name == "ادمین"
        or obj_current.name == "نماینده"
        or obj_current.name == "پذیرنده"
        or obj_current.name == "سازمان"
        or obj_current.name == "کاربر ساده"
    ):
        raise RoleNotFoundException()
    # * Verify role's name duplicate
    await role_crud.verify_duplicate_name(
        db=db,
        name=update_data.data.name,
        exception_name=obj_current.name,
    )
    # * Update role
    role = await role_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.UPDATE_ROLE,
        detail="نقش {} با موفقیت توسط کاربر {} ویرایش شد".format(
            role.name,
            current_user.national_code,
        ),
    )

    return role


# ---------------------------------------------------------------------------
@router.post("/list", response_model=list[RoleRead])
async def get_roles_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_ROLE]),
    ),
    filter_data: RoleFilter,
    skip: int = 0,
    limit: int = 10,
) -> list[RoleRead]:
    """
    ! Get All Role

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
    role_list
        List of role

    """
    # * Prepare filter fields
    filter_data.name = (
        Role.name.contains(filter_data.name) if filter_data.name is not None else True
    )
    # * Add filter fields
    query = (
        select(Role)
        .filter(
            or_(filter_data.name),
        )
        .order_by(Role.created_at.desc())
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == RoleFilterOrderFild.name:
                query = query.order_by(Role.name.desc())
            elif field == RoleFilterOrderFild.created_at:
                query = query.order_by(Role.created_at.desc())
            elif field == RoleFilterOrderFild.updated_at:
                query = query.order_by(Role.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == RoleFilterOrderFild.name:
                query = query.order_by(Role.name.asc())
            elif field == RoleFilterOrderFild.created_at:
                query = query.order_by(Role.created_at.asc())
            elif field == RoleFilterOrderFild.updated_at:
                query = query.order_by(Role.updated_at.asc())
    # * Find All agent with filters
    role_list = await role_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return role_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=RoleRead)
async def get_role(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_ROLE]),
    ),
    obj_data: IDRequest,
) -> RoleRead:
    """
    ! Find Role

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target Ability's ID

    Returns
    -------
    obj
        Found Role

    Raises
    ------
    RoleNotFoundException
    """
    # * Verify ability existence
    obj = await role_crud.verify_existence(db=db, role_id=obj_data.id)
    return obj


# ---------------------------------------------------------------------------
@router.post(
    "/add_permissions",
    response_model=ResultResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_permissions_to_role(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.ASSIGN_ROLE]),
    ),
    data: PermissionsToRole,
) -> ResultResponse:
    """
    ! Add permission to role

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    data
        Necessary data

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    RoleNotFoundException

    """
    # * Verify role existence
    role = await role_crud.verify_existence(db=db, role_id=data.role_id)

    # * Get All Permissions
    permissions = await permission_crud.get_by_ids(db=db, list_ids=data.permission_ids)
    for perm in permissions:
        # ? Find RoelPermission
        role_perm = await role_permission_crud.verify_permission_by_role_id(
            db=db,
            role_id=role.id,
            permission_id=perm.id,
        )
        # * Create If not existence
        if not role_perm:
            create_data = RolePermissionCreate(role_id=role.id, permission_id=perm.id)
            await role_permission_crud.create(db=db, obj_in=create_data)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.ASSIGN_PERMISSION_TO_ROLE,
        detail="دسترسی های نقش {} با موفقیت توسط کاربر {} ویرایش شد".format(
            role.name,
            current_user.national_code,
        ),
    )

    return ResultResponse(result="Permissions Added Successfully")


# ---------------------------------------------------------------------------
@router.get(path="/me", response_model=RoleReadV2)
async def me(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> RoleReadV2:
    """
    ! Get My Role Data

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user object

    Returns
    -------
    role
        My Role data

    Raises
    ------
    RoleNotFoundException
    """
    # * Get role requester role id
    role = await role_crud.verify_existence(db=db, role_id=current_user.role_id)

    response = RoleReadV2(
        id=role.id,
        name=role.name,
        is_valid=current_user.is_valid,
    )
    return response
