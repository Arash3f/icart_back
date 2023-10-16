from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import and_, select

from src import deps
from src.organization.crud import organization as organization_crud
from src.organization.models import Organization
from src.organization.schema import (
    OrganizationRead,
    OrganizationFilter,
    OrganizationFilterOrderFild,
)
from src.schema import IDRequest
from src.user.models import User
from src.permission import permission_codes as permission

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/organization", tags=["organization"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=OrganizationRead)
async def find_organization(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_ORGANIZATION]),
    ),
    obj_data: IDRequest,
) -> OrganizationRead:
    """
    ! Get one Organization

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target Organization's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    OrganizationNotFoundException
    """
    # * Verify organization existence
    obj = await organization_crud.verify_existence(db=db, organization_id=obj_data.id)

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[OrganizationRead])
async def get_organization(
    *,
    db=Depends(deps.get_db),
    filter_data: OrganizationFilter,
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_ORGANIZATION]),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[OrganizationRead]:
    """
    ! Get All Organization

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    filter_data
        Filter data
    skip
        Pagination skip
    limit
        Pagination limit

    Returns
    -------
    obj_list
        List of organization
    """
    # * Prepare filter fields
    filter_data.location_id = (
        (Organization.location_id == filter_data.location_id)
        if filter_data.location_id
        else True
    )
    filter_data.user_id = (
        (Organization.user_id == filter_data.user_id) if filter_data.user_id else True
    )
    filter_data.agent_id = (
        (Organization.agent_id == filter_data.agent_id)
        if filter_data.agent_id
        else True
    )

    # * Add filter fields
    query = select(Organization).filter(
        and_(
            filter_data.location_id,
            filter_data.user_id,
            filter_data.agent_id,
        ),
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == OrganizationFilterOrderFild.agent_id:
                query = query.order_by(Organization.agent_id.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == OrganizationFilterOrderFild.agent_id:
                query = query.order_by(Organization.agent_id.asc())
    # * Find All agent with filters
    obj_list = await organization_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list


# ---------------------------------------------------------------------------
@router.get("/me", response_model=OrganizationRead)
async def me(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> OrganizationRead:
    organization = await organization_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )
    return organization
