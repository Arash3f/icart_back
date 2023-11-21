from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from src import deps
from src.location.crud import location as location_crud
from src.log.crud import log as log_crud
from src.location.models import Location
from src.location.schema import (
    LocationCreate,
    LocationFilter,
    LocationRead,
    LocationUpdate,
    LocationFilterOrderFild,
    LocationCompleteRead,
)
from src.log.models import LogType
from src.permission import permission_codes as permission
from src.schema import IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/location", tags=["location"])


# ---------------------------------------------------------------------------
@router.post(path="/create", response_model=LocationRead)
async def create_location(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CREATE_LOCATION]),
    ),
    create_data: LocationCreate,
) -> LocationRead:
    """
    ! Create Location

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    create_data
        Necessary data for create location

    Returns
    -------
    obj
        New location

    Raises
    ------
    LocationNameIsDuplicatedException
    LocationParentNotFoundException
    LocationNotFoundException
    """
    # * Verify parent existence
    if create_data.parent_id:
        await location_crud.verify_existence(
            db=db,
            location_id=create_data.parent_id,
            parent_exception=True,
        )
    # * Verify location name duplicate
    await location_crud.verify_duplicate_name(db=db, name=create_data.name)

    obj = await location_crud.create(db=db, obj_in=create_data)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.ADD_LOCATION,
        user_id=current_user.id,
        detail="منطقه {} با موفقیت توسط کاربر {} ساخته شد".format(
            obj.name,
            current_user.id,
        ),
    )

    return obj


# ---------------------------------------------------------------------------
@router.put(path="/update", response_model=LocationRead)
async def update_location(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_LOCATION]),
    ),
    update_data: LocationUpdate,
) -> LocationRead:
    """
    ! Update Location

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update location

    Returns
    -------
    obj
        Updated location

    Raises
    ------
    LocationNameIsDuplicatedException
    LocationParentNotFoundException
    LocationNotFoundException
    """
    # * Verify location existence
    obj_current = await location_crud.verify_existence(
        db=db,
        location_id=update_data.where.id,
    )
    # * Verify parent existence
    if update_data.data.parent_id:
        await location_crud.verify_existence(
            db=db,
            location_id=update_data.data.parent_id,
            parent_exception=True,
        )
    # * Verify location name duplicate
    await location_crud.verify_duplicate_name(
        db=db,
        name=update_data.data.name,
        exception_name=obj_current.name,
    )

    obj = await location_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.UPDATE_LOCATION,
        user_id=current_user.id,
        detail="منطقه {} با موفقیت توسط کاربر {} ویرایش شد".format(
            obj.name,
            current_user.id,
        ),
    )
    return obj


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=LocationRead)
async def find_location(
    *,
    db=Depends(deps.get_db),
    obj_data: IDRequest,
) -> LocationRead:
    """
    ! Find Location

    Parameters
    ----------
    db
        Target database connection
    obj_data
        Target Location's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    LocationNotFoundException
    """
    # * Verify location existence
    obj = await location_crud.verify_existence(db=db, location_id=obj_data.id)

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[LocationRead])
async def get_location_list(
    *,
    db=Depends(deps.get_db),
    filter_data: LocationFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[LocationRead]:
    """
    ! Get All Location

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
    is_main = True
    if filter_data.is_main is not None:
        if filter_data.is_main:
            is_main = Location.parent_id.is_(None)
        else:
            is_main = Location.parent_id.is_not(None)

    filter_data.parent_id = (
        (Location.parent_id == filter_data.parent_id)
        if filter_data.parent_id is not None
        else True
    )
    filter_data.name = (
        (Location.name.contains(filter_data.name))
        if filter_data.name is not None
        else True
    )

    # * Add filter fields
    query = (
        select(Location)
        .filter(
            and_(
                is_main,
                filter_data.parent_id,
                filter_data.name,
            ),
        )
        .order_by(Location.created_at.desc())
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == LocationFilterOrderFild.is_main:
                query = query.order_by(Location.is_main.desc())
            elif field == LocationFilterOrderFild.name:
                query = query.order_by(Location.name.desc())
            elif field == LocationFilterOrderFild.parent_id:
                query = query.order_by(Location.parent_id.desc())
            elif field == LocationFilterOrderFild.created_at:
                query = query.order_by(Location.created_at.desc())
            elif field == LocationFilterOrderFild.updated_at:
                query = query.order_by(Location.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == LocationFilterOrderFild.is_main:
                query = query.order_by(Location.is_main.asc())
            elif field == LocationFilterOrderFild.name:
                query = query.order_by(Location.name.asc())
            elif field == LocationFilterOrderFild.parent_id:
                query = query.order_by(Location.parent_id.asc())
            elif field == LocationFilterOrderFild.created_at:
                query = query.order_by(Location.created_at.asc())
            elif field == LocationFilterOrderFild.updated_at:
                query = query.order_by(Location.updated_at.asc())
    # * Find All agent with filters
    obj_list = await location_crud.get_multi(db=db, skip=skip, limit=limit, query=query)

    return obj_list


# ---------------------------------------------------------------------------
@router.post(path="/list/complete", response_model=List[LocationCompleteRead])
async def get_compelete_location_list(
    *,
    db=Depends(deps.get_db),
    filter_data: LocationFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[LocationCompleteRead]:
    """
    ! Get All Location

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
    is_main = Location.parent_id.is_(None)

    filter_data.parent_id = (
        (Location.parent_id == filter_data.parent_id)
        if filter_data.parent_id is not None
        else True
    )
    filter_data.name = (
        (Location.name.contains(filter_data.name))
        if filter_data.name is not None
        else True
    )

    # * Add filter fields
    query = (
        select(Location)
        .filter(
            and_(
                is_main,
                filter_data.parent_id,
                filter_data.name,
            ),
        )
        .order_by(Location.created_at.desc())
    ).options(selectinload(Location.children))
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == LocationFilterOrderFild.is_main:
                query = query.order_by(Location.is_main.desc())
            elif field == LocationFilterOrderFild.name:
                query = query.order_by(Location.name.desc())
            elif field == LocationFilterOrderFild.parent_id:
                query = query.order_by(Location.parent_id.desc())
            elif field == LocationFilterOrderFild.created_at:
                query = query.order_by(Location.created_at.desc())
            elif field == LocationFilterOrderFild.updated_at:
                query = query.order_by(Location.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == LocationFilterOrderFild.is_main:
                query = query.order_by(Location.is_main.asc())
            elif field == LocationFilterOrderFild.name:
                query = query.order_by(Location.name.asc())
            elif field == LocationFilterOrderFild.parent_id:
                query = query.order_by(Location.parent_id.asc())
            elif field == LocationFilterOrderFild.created_at:
                query = query.order_by(Location.created_at.asc())
            elif field == LocationFilterOrderFild.updated_at:
                query = query.order_by(Location.updated_at.asc())
    # * Find All agent with filters
    obj_list = await location_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return obj_list
