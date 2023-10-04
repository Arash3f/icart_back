from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select

from src import deps
from src.location.crud import location as location_crud
from src.location.models import Location
from src.location.schema import (
    LocationCreate,
    LocationFilter,
    LocationRead,
    LocationUpdate,
)
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
    return obj


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=LocationRead)
async def find_location(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    obj_data: IDRequest,
) -> LocationRead:
    """
    ! Find Location

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
    LocationNotFoundException
    """
    # * Verify location existence
    obj = await location_crud.verify_existence(db=db, location_id=obj_data.id)

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[LocationRead])
async def get_location(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
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
    obj_list
        List of ability
    """
    # * Prepare filter fields
    filter_data.is_main = (
        (Location.parent_id.is_(None)) if filter_data.is_main else False
    )
    # * Add filter fields
    query = select(Location).filter(
        or_(
            filter_data.return_all,
            filter_data.is_main,
        ),
    )
    # * Find All agent with filters
    obj_list = await location_crud.get_multi(db=db, skip=skip, limit=limit, query=query)

    return obj_list
