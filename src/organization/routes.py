from typing import List

from fastapi import APIRouter, Depends

from src import deps
from src.organization.crud import organization as organization_crud
from src.organization.schema import OrganizationRead
from src.schema import IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/organization", tags=["organization"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=OrganizationRead)
async def find_organization(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
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
    # ? Verify organization existence
    obj = await organization_crud.verify_existence(db=db, organization_id=obj_data.id)

    return obj


# ---------------------------------------------------------------------------
@router.get(path="/list", response_model=List[OrganizationRead])
async def get_organization(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> List[OrganizationRead]:
    """
    ! Get All Organization

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User

    Returns
    -------
    obj_list
        List of organization
    """
    obj_list = await organization_crud.get_multi(db=db)
    return obj_list
