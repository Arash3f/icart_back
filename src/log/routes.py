from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, or_

from src import deps
from src.log.crud import log as log_crud
from src.log.models import Log
from src.log.schema import (
    LogFilter,
    LogRead,
    LogFilterOrderFild,
)
from src.permission import permission_codes as permission
from src.schema import IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/log", tags=["log"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=LogRead)
async def find_log(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_LOG]),
    ),
    obj_data: IDRequest,
) -> LogRead:
    """
    ! Find Log

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target Log's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    LogNotFoundException
    """
    # * Verify log existence
    obj = await log_crud.verify_existence(db=db, log_id=obj_data.id)

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[LogRead])
async def get_log(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_LOG]),
    ),
    filter_data: LogFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[LogRead]:
    """
    ! Get All Log

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
        List of logs
    """
    # * Prepare filter fields
    filter_data.name = (
        or_(
            User.first_name.contains(filter_data.name),
            User.last_name.contains(filter_data.name),
        )
        if filter_data.name is not None
        else True
    )
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code is not None
        else True
    )
    filter_data.type = (Log.type == filter_data.type) if filter_data.type else True

    # * Add filter fields
    query = (
        select(Log)
        .filter(
            and_(
                filter_data.name,
                filter_data.national_code,
                filter_data.type,
            ),
        )
        .join(Log.user)
        .order_by(Log.created_at.desc())
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == LogFilterOrderFild.is_main:
                query = query.order_by(Log.type.desc())
            elif field == LogFilterOrderFild.type:
                query = query.order_by(Log.created_at.desc())
            elif field == LogFilterOrderFild.created_at:
                query = query.order_by(Log.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == LogFilterOrderFild.is_main:
                query = query.order_by(Log.type.asc())
            elif field == LogFilterOrderFild.type:
                query = query.order_by(Log.created_at.asc())
            elif field == LogFilterOrderFild.created_at:
                query = query.order_by(Log.updated_at.asc())
    # * Find All agent with filters
    obj_list = await log_crud.get_multi(db=db, skip=skip, limit=limit, query=query)

    return obj_list
