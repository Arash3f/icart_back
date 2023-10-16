from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_

from src import deps
from src.merchant.crud import merchant as merchant_crud
from src.merchant.models import Merchant
from src.merchant.schema import MerchantRead, MerchantFilter, MerchantFilterOrderFild
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/merchant", tags=["merchant"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=MerchantRead)
async def get_merchant(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    item_id: UUID,
) -> MerchantRead:
    """
    ! Find Merchant

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    item_id
        Target Merchant's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    MerchantNotFoundException
    """
    # ? Verify merchant existence
    obj = await merchant_crud.verify_existence(db=db, merchant_id=item_id)

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[MerchantRead])
async def get_merchant_list(
    *,
    db=Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20,
    filter_data: MerchantFilter,
) -> List[MerchantRead]:
    """
    ! Get All Merchant

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
        List of merchants
    """
    # * Prepare filter fields
    filter_data.location_id = (
        (Merchant.location_id == filter_data.location_id)
        if filter_data.location_id
        else True
    )
    filter_data.selling_type = (
        (Merchant.selling_type == filter_data.selling_type)
        if filter_data.selling_type
        else True
    )

    # * Add filter fields
    query = select(Merchant).filter(
        and_(
            filter_data.location_id,
            filter_data.selling_type,
        ),
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == MerchantFilterOrderFild.created_at:
                query = query.order_by(Merchant.created_at.desc())
            # elif field == MerchantFilterOrderFild.name:
            #     query = query.order_by(Merchant.name.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == MerchantFilterOrderFild.created_at:
                query = query.order_by(Merchant.created_at.asc())
            # elif field == MerchantFilterOrderFild.name:
            #     query = query.order_by(Merchant.name.asc())
    obj_list = await merchant_crud.get_multi(db=db, skip=skip, limit=limit)
    return obj_list


# ---------------------------------------------------------------------------
@router.get(path="/me", response_model=MerchantRead)
async def me(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> MerchantRead:
    """
    ! Get My Merchant Data

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User

    Returns
    -------
    obj
        Found merchant

    Raises
    ------
    MerchantNotFoundException
    """
    obj = await merchant_crud.find_by_user_id(db=db, user_id=current_user.id)
    return obj
