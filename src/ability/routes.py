from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_

from src import deps
from src.ability.crud import ability as ability_crud
from src.ability.models import Ability
from src.ability.schema import (
    AbilityCreate,
    AbilityFilter,
    AbilityFilterOrderFild,
    AbilityRead,
    AbilityUpdate,
)
from src.agent.crud import agent as agent_crud
from src.log.crud import log as log_crud
from src.log.models import LogType
from src.schema import DeleteResponse, IDRequest
from src.user.models import User
from src.permission import permission_codes as permission

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/ability", tags=["ability"])


# ---------------------------------------------------------------------------
@router.delete(path="/delete", response_model=DeleteResponse)
async def delete_ability(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.DELETE_ABILITY]),
    ),
    delete_data: IDRequest,
) -> DeleteResponse:
    """
    ! Delete Ability

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user object
    delete_data
        Ability id

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    AbilityNotFoundException
    CanNotUpdateBaseAbilityException
    """
    # * Verify ability existence
    ability = await ability_crud.verify_existence(db=db, ability_id=delete_data.id)

    # * Delete Ability
    await ability_crud.delete(db=db, item_id=delete_data.id)
    # ? Update All Agent profit_rate and is_main field
    await agent_crud.update_auto_data(db=db)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.DELETE_ABILITY,
        detail="توانایی نماینده {} با موفقیت توسط کاربر {} حذف شد".format(
            ability.name,
            current_user.username,
        ),
    )

    return DeleteResponse(result="Ability Deleted Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/create", response_model=AbilityRead)
async def create_ability(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CREATE_ABILITY]),
    ),
    create_data: AbilityCreate,
) -> AbilityRead:
    """
    ! Create New Ability

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user object
    create_data
        Necessary data for create ability

    Returns
    -------
    ability
        New ability

    Raises
    ------
    AbilityNameIsDuplicatedException
    """
    # * Verify ability name duplicate
    await ability_crud.verify_duplicate_name(db=db, name=create_data.name)
    # * Create Ability
    ability = await ability_crud.create(db=db, obj_in=create_data)
    # ? Update All Agent profit_rate and is_main field
    await agent_crud.update_auto_data(db=db)
    await db.refresh(ability)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.ADD_ROLE,
        user_id=current_user.id,
        detail="توانایی نماینده {} با موفقیت توسط کاربر {} ساخته شد".format(
            ability.name,
            current_user.username,
        ),
    )
    return ability


# ---------------------------------------------------------------------------
@router.put(path="/update", response_model=AbilityRead)
async def update_ability(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_ABILITY]),
    ),
    update_data: AbilityUpdate,
) -> AbilityRead:
    """
    ! Update Ability

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user object
    update_data
        Necessary data for update ability

    Returns
    -------
    ability
        Updated ability

    Raises
    ------
    AbilityNotFoundException
    AbilityNameIsDuplicatedException
    CanNotUpdateBaseAbilityException
    """
    # * Verify ability existence
    obj_current = await ability_crud.verify_existence(
        db=db,
        ability_id=update_data.where.id,
    )

    # * Verify ability name duplicate
    await ability_crud.verify_duplicate_name(
        db=db,
        name=update_data.data.name,
        exception_name=obj_current.name,
    )
    # * Update ability
    ability = await ability_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.UPDATE_ABILITY,
        user_id=current_user.id,
        detail="توانایی نماینده {} با موفقیت توسط کاربر {} ویرایش شد".format(
            ability.name,
            current_user.username,
        ),
    )
    return ability


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=AbilityRead)
async def find_ability(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_ABILITY]),
    ),
    obj_data: IDRequest,
) -> AbilityRead:
    """
    ! Find Ability

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user object
    obj_data
        Target ability id

    Returns
    -------
    ability
        Found ability

    Raises
    ------
    AbilityNotFoundException
    """
    # * Verify ability existence
    ability = await ability_crud.verify_existence(db=db, ability_id=obj_data.id)

    return ability


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[AbilityRead])
async def ability_list(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_ABILITY]),
    ),
    filter_data: AbilityFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[AbilityRead]:
    """
    ! Find All Ability

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user object
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
    filter_data.name = (
        Ability.name.contains(filter_data.name) if filter_data.name else True
    )
    # * Add filter fields
    query = (
        select(Ability)
        .filter(
            and_(
                filter_data.name,
            ),
        )
        .order_by(Ability.created_at.desc())
    )

    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == AbilityFilterOrderFild.name:
                query = query.order_by(Ability.name.desc())
            elif field == AbilityFilterOrderFild.created_at:
                query = query.order_by(Ability.created_at.desc())
            elif field == AbilityFilterOrderFild.updated_at:
                query = query.order_by(Ability.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == AbilityFilterOrderFild.name:
                query = query.order_by(Ability.name.asc())
            elif field == AbilityFilterOrderFild.created_at:
                query = query.order_by(Ability.created_at.asc())
            elif field == AbilityFilterOrderFild.updated_at:
                query = query.order_by(Ability.updated_at.asc())
    # * Find All ability with filters
    obj_list = await ability_crud.get_multi(db=db, skip=skip, limit=limit, query=query)

    return obj_list
