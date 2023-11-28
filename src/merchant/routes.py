from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, or_, orm, func
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.agent.models import Agent
from src.contract.models import Contract
from src.log.models import LogType
from src.merchant.crud import merchant as merchant_crud
from src.log.crud import log as log_crud
from src.agent.crud import agent as agent_crud
from src.merchant.models import Merchant
from src.merchant.schema import (
    MerchantRead,
    MerchantFilter,
    MerchantFilterOrderFild,
    StoresRead,
    MerchantUpdate,
    MerchantReadV2,
    MerchantAggregateRead,
)
from src.schema import ResultResponse, UpdateActivityRequest
from src.user.models import User
from src.permission import permission_codes as permission

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/merchant", tags=["merchant"])


# ---------------------------------------------------------------------------
@router.put("/update", response_model=MerchantRead)
async def update_merchant(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_MERCHANT]),
    ),
    update_data: MerchantUpdate,
) -> MerchantRead:
    """
    ! Update Merchant profits

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update profits

    Returns
    -------
    merchant
        Updated merchant

    Raises
    ------
    MerchantNotFoundException
    """
    # * Verify merchant existence
    obj_current = await merchant_crud.verify_existence(
        db=db,
        merchant_id=update_data.where.id,
    )

    obj_current.blue_profit = update_data.data.blue_profit
    obj_current.silver_profit = update_data.data.silver_profit
    obj_current.gold_profit = update_data.data.gold_profit
    obj_current.gold_profit = update_data.data.gold_profit

    # * Update merchant
    db.add(obj_current)
    await db.commit()
    await db.refresh(obj_current)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.UPDATE_MERCHANT,
        user_id=current_user.id,
        detail="پذیرنده {} با موفقیت توسط کاربر {} ویرایش شد".format(
            obj_current.user.username,
            current_user.username,
        ),
    )

    return obj_current


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=MerchantRead)
async def get_merchant(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user(),
    ),
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
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_MERCHANT]),
    ),
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
    filter_data.name = (
        or_(
            Contract.name.contains(filter_data.name),
        )
        if filter_data.name is not None
        else True
    )
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code is not None
        else True
    )
    filter_data.location_id = (
        (Merchant.location_id == filter_data.location_id)
        if filter_data.location_id is not None
        else True
    )
    filter_data.selling_type = (
        (Merchant.selling_type == filter_data.selling_type)
        if filter_data.selling_type
        else True
    )
    filter_data.field_of_work = (
        (Merchant.field_of_work == filter_data.field_of_work)
        if filter_data.field_of_work is not None
        else True
    )
    filter_data.is_active = (
        (Merchant.is_active == filter_data.is_active)
        if filter_data.is_active is not None
        else True
    )
    filter_data.user_id = (
        (Merchant.user_id == filter_data.user_id)
        if filter_data.user_id is not None
        else True
    )
    filter_data.agent_id = (
        (Merchant.agent_id == filter_data.agent_id)
        if filter_data.agent_id is not None
        else True
    )

    # * Add filter fields
    query = (
        select(Merchant)
        .filter(
            and_(
                filter_data.is_active,
                filter_data.location_id,
                filter_data.name,
                filter_data.national_code,
                filter_data.selling_type,
                filter_data.user_id,
                filter_data.agent_id,
                filter_data.field_of_work,
            ),
        )
        .join(Merchant.user)
        .join(Merchant.contract)
    ).order_by(Merchant.created_at)

    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == MerchantFilterOrderFild.created_at:
                query = query.order_by(Merchant.created_at.desc())
            elif field == MerchantFilterOrderFild.updated_at:
                query = query.order_by(Merchant.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == MerchantFilterOrderFild.created_at:
                query = query.order_by(Merchant.created_at.asc())
            elif field == MerchantFilterOrderFild.updated_at:
                query = query.order_by(Merchant.updated_at.asc())
    obj_list = await merchant_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return obj_list


# ---------------------------------------------------------------------------
@router.post(path="/stores", response_model=List[StoresRead])
async def get_stores(
    *,
    db=Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20,
    filter_data: MerchantFilter,
) -> List[StoresRead]:
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
    filter_data.name = (
        or_(
            Contract.name.contains(filter_data.name),
        )
        if filter_data.name is not None
        else True
    )
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code),)
        if filter_data.national_code is not None
        else True
    )
    filter_data.location_id = (
        (Merchant.location_id == filter_data.location_id)
        if filter_data.location_id is not None
        else True
    )
    filter_data.selling_type = (
        (Merchant.selling_type == filter_data.selling_type)
        if filter_data.selling_type
        else True
    )
    filter_data.field_of_work = (
        (Merchant.field_of_work == filter_data.field_of_work)
        if filter_data.field_of_work is not None
        else True
    )
    filter_data.is_active = (
        (Merchant.is_active == filter_data.is_active)
        if filter_data.is_active is not None
        else True
    )
    filter_data.user_id = (
        (Merchant.user_id == filter_data.user_id)
        if filter_data.user_id is not None
        else True
    )
    filter_data.agent_id = (
        (Merchant.agent_id == filter_data.agent_id)
        if filter_data.agent_id is not None
        else True
    )

    # * Add filter fields
    query = (
        select(Merchant)
        .filter(
            and_(
                Merchant.is_active == True,
                filter_data.location_id,
                filter_data.name,
                filter_data.national_code,
                filter_data.selling_type,
                filter_data.user_id,
                filter_data.agent_id,
                filter_data.field_of_work,
            ),
        )
        .join(Merchant.user)
        .join(Merchant.contract)
    ).order_by(Merchant.created_at)

    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == MerchantFilterOrderFild.created_at:
                query = query.order_by(Merchant.created_at.desc())
            elif field == MerchantFilterOrderFild.updated_at:
                query = query.order_by(Merchant.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == MerchantFilterOrderFild.created_at:
                query = query.order_by(Merchant.created_at.asc())
            elif field == MerchantFilterOrderFild.updated_at:
                query = query.order_by(Merchant.updated_at.asc())
    obj_list = await merchant_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return obj_list


# ---------------------------------------------------------------------------
@router.post(path="/stores/find", response_model=MerchantReadV2)
async def get_merchant(
    *,
    db=Depends(deps.get_db),
    item_id: UUID,
) -> MerchantReadV2:
    """
    ! Find Merchant

    Parameters
    ----------
    db
        Target database connection
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


# ---------------------------------------------------------------------------
@router.get(path="/aggregate/information", response_model=list[MerchantAggregateRead])
async def aggregate_information(
    *,
    db=Depends(deps.get_db),
) -> list[MerchantAggregateRead]:
    """
    ! Get Merchant Aggregate information

    Parameters
    ----------
    db
        Target database connection

    Returns
    -------
    obj
        Calculate items by field of work
    """
    result = await db.execute(
        select(
            func.count(Merchant.id).label("count"),
            Merchant.field_of_work.label("field_of_work"),
        )
        .select_from(Merchant)
        .group_by(Merchant.field_of_work),
    )

    res = result.all()
    return res


# ---------------------------------------------------------------------------
@router.put(path="/update/activity", response_model=ResultResponse)
async def update_user_activity(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_ORGANIZATION]),
    ),
    update_data: UpdateActivityRequest,
) -> ResultResponse:
    """
    ! Update Merchant Activity

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update Merchant

    Returns
    -------
    obj
        Updated Merchant

    Raises
    ------
    UserNotFoundException
    """
    # * Verify user existence
    obj = await merchant_crud.verify_existence(
        db=db,
        merchant_id=update_data.where.id,
    )

    obj.is_active = update_data.data.is_active
    db.add(obj)
    await db.commit()

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.UPDATE_USER_ACTIVITY,
        detail="وضعیت پذینده {} با موفقیت توسط کاربر {} ویرایش شد".format(
            obj.contract.position_request.name,
            current_user.username,
        ),
    )

    return ResultResponse(result="Merchant Activity Updated Successfully")
