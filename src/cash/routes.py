from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select

from src import deps
from src.cash.crud import cash as cash_crud
from src.cash.models import Cash
from src.cash.schema import CashFilter, CashFilterOrderFild, CashRead
from src.permission import permission_codes as permission
from src.schema import IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/cash", tags=["cash"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=CashRead)
async def get_cash(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_WALLET]),
    ),
    obj_data: IDRequest,
) -> CashRead:
    """
    ! Find Cash

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target Cash's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    CashNotFoundException
    """
    # * Verify cash existence
    obj = await cash_crud.verify_existence(db=db, cash_id=obj_data.id)

    return obj


# ---------------------------------------------------------------------------
@router.get(path="/my", response_model=CashRead)
async def get_cash_my(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> CashRead:
    """
    ! Get My Cash

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
    CashNotFoundException
    """
    cash = await cash_crud.verify_existence(db=db, cash_id=current_user.cash_id)
    return cash


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[CashRead])
async def get_list_cash(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_WALLET]),
    ),
    filter_data: CashFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[CashRead]:
    """
    ! Get All Cash

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
    # * Add filter fields
    query = select(Cash).filter().order_by(Cash.created_at.desc())

    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == CashFilterOrderFild.received:
                query = query.order_by(Cash.received.desc())
            elif field == CashFilterOrderFild.consumed:
                query = query.order_by(Cash.consumed.desc())
            elif field == CashFilterOrderFild.remaining:
                query = query.order_by(Cash.remaining.desc())
            elif field == CashFilterOrderFild.transferred:
                query = query.order_by(Cash.transferred.desc())
            elif field == CashFilterOrderFild.debt:
                query = query.order_by(Cash.debt.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == CashFilterOrderFild.received:
                query = query.order_by(Cash.received.asc())
            elif field == CashFilterOrderFild.consumed:
                query = query.order_by(Cash.consumed.asc())
            elif field == CashFilterOrderFild.remaining:
                query = query.order_by(Cash.remaining.asc())
            elif field == CashFilterOrderFild.transferred:
                query = query.order_by(Cash.transferred.asc())
            elif field == CashFilterOrderFild.debt:
                query = query.order_by(Cash.debt.asc())
    # * Find All ability with filters
    obj_list = await cash_crud.get_multi(db=db, skip=skip, limit=limit)
    return obj_list
