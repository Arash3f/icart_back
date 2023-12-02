from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, or_, and_

from src import deps
from src.credit.crud import credit as credit_crud
from src.credit.models import Credit
from src.credit.schema import CreditFilter, CreditFilterOrderFild, CreditRead
from src.permission import permission_codes as permission
from src.schema import IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/credit", tags=["credit"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=CreditRead)
async def get_credit(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_WALLET]),
    ),
    obj_data: IDRequest,
) -> CreditRead:
    """
    ! Find Credit

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target Credit's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    CreditNotFoundException
    """
    # * Verify credit existence
    obj = await credit_crud.verify_existence(db=db, credit_id=obj_data.id)

    return obj


# ---------------------------------------------------------------------------
@router.get(path="/my", response_model=CreditRead)
async def get_credit_my(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> CreditRead:
    """
    ! Get My Credit

    Parameters
    ----------
    db
        Target database connection
    current_user
        Required permissions

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    CreditNotFoundException
    """
    credit = await credit_crud.verify_existence(db=db, credit_id=current_user.credit_id)
    return credit


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[CreditRead])
async def get_list_credit(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_WALLET]),
    ),
    filter_data: CreditFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[CreditRead]:
    """
    ! Get All Credit

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
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code is not None
        else True
    )
    filter_data.phone_number = (
        (User.phone_number.contains(filter_data.phone_number))
        if filter_data.phone_number is not None
        else True
    )
    filter_data.name = (
        or_(
            User.first_name.contains(filter_data.name),
        )
        if filter_data.name is not None
        else True
    )
    filter_data.last_name = (
        or_(
            User.last_name.contains(filter_data.last_name),
        )
        if filter_data.last_name is not None
        else True
    )

    # * Add filter fields
    query = (
        select(Credit)
        .filter(
            and_(
                filter_data.phone_number,
                filter_data.national_code,
                filter_data.name,
                filter_data.last_name,
            ),
        )
        .join(Credit.user)
        .order_by(Credit.created_at.desc())
    )

    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == CreditFilterOrderFild.received:
                query = query.order_by(Credit.received.desc())
            elif field == CreditFilterOrderFild.consumed:
                query = query.order_by(Credit.consumed.desc())
            elif field == CreditFilterOrderFild.remaining:
                query = query.order_by(Credit.remaining.desc())
            elif field == CreditFilterOrderFild.transferred:
                query = query.order_by(Credit.transferred.desc())
            elif field == CreditFilterOrderFild.debt:
                query = query.order_by(Credit.debt.desc())
            elif field == CreditFilterOrderFild.created_at:
                query = query.order_by(Credit.created_at.desc())
            elif field == CreditFilterOrderFild.updated_at:
                query = query.order_by(Credit.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == CreditFilterOrderFild.received:
                query = query.order_by(Credit.received.asc())
            elif field == CreditFilterOrderFild.consumed:
                query = query.order_by(Credit.consumed.asc())
            elif field == CreditFilterOrderFild.remaining:
                query = query.order_by(Credit.remaining.asc())
            elif field == CreditFilterOrderFild.transferred:
                query = query.order_by(Credit.transferred.asc())
            elif field == CreditFilterOrderFild.debt:
                query = query.order_by(Credit.debt.asc())
            elif field == CreditFilterOrderFild.created_at:
                query = query.order_by(Credit.created_at.asc())
            elif field == CreditFilterOrderFild.updated_at:
                query = query.order_by(Credit.updated_at.asc())
    # * Find All ability with filters
    obj_list = await credit_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return obj_list
