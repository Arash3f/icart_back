from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.organization.crud import organization as organization_crud
from src.organization.schema import OrganizationRead
from src.schema import IDRequest
from src.transaction.models import Transaction
from src.user.crud import user as user_crud
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


# ---------------------------------------------------------------------------
@router.get("/me", response_model=OrganizationRead)
async def get_organization_me(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
):
    organization = organization_crud.get(db=db, id=current_user.self_organization_id)
    return organization


# ---------------------------------------------------------------------------
@router.get("/additional_info")
async def get_organization_additional_info(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
):
    users_query = select(User).where(
        User.organization_id == current_user.self_organization_id,
    )
    users = await user_crud.get_multi(db=db, query=users_query)
    users_id = [user.id for user in users]
    transaction_count = await db.execute(
        select(func.count())
        .select_from(Transaction)
        .where(
            or_(
                Transaction.transferor_id.in_(users_id),
                Transaction.receiver_id.in_(users_id),
            ),
        )
        .group_by(func.month(Transaction.created_at), func.year(Transaction.created_at))
        .subquery(),
    )
    return {
        "Users count": len(users_id),
        "Transaction count": transaction_count.scalar_one(),
    }
