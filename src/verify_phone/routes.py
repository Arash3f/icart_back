from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.core.config import settings
from src.permission import permission_codes as permission
from src.schema import IDRequest, ResultResponse
from src.user.models import User
from src.utils.sms import send_verify_phone_sms
from src.verify_phone.crud import verify_phone as verify_phone_crud
from src.verify_phone.models import VerifyPhone
from src.verify_phone.schema import (
    VerifyPhoneFilter,
    VerifyPhoneNumberRequestIn,
    VerifyPhoneRead,
)

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/verify_phone", tags=["verify_phone"])


# ---------------------------------------------------------------------------
@router.post("/verify", response_model=ResultResponse, status_code=200)
async def verify_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    request_data: VerifyPhoneNumberRequestIn,
) -> ResultResponse:
    """
    ! Send Verify Code To Phone Number

    Parameters
    ----------
    db
        Target database connection
    request_data
        Necessary data for Send code

    Returns
    -------
    response
        Result of operation
    """
    phone_number = request_data.phone_number
    # * Generate dynamic code
    code = await verify_phone_crud.generate_dynamic_code(db=db)
    # * Find phone number
    verify = await verify_phone_crud.find_by_phone_number(
        db=db,
        phone_number=phone_number,
    )
    # ? Update verify phone
    expiration_code_at = datetime.now() + timedelta(
        minutes=settings.DYNAMIC_PASSWORD_EXPIRE_MINUTES,
    )
    if not verify:
        verify = VerifyPhone()
        verify.phone_number = phone_number

    verify.verify_code = code
    verify.expiration_code_at = expiration_code_at
    # ! Send SMS to phone number
    send_verify_phone_sms(
        phone_number=phone_number,
        code=code,
        exp_time=expiration_code_at,
    )
    db.add(verify)
    await db.commit()
    return ResultResponse(result="Code sent successfully")


# ---------------------------------------------------------------------------
@router.post("/list", response_model=list[VerifyPhoneRead])
async def verify_phone_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_VERIFY_PHONE]),
    ),
    filter_data: VerifyPhoneFilter,
    skip: int = 0,
    limit: int = 20,
) -> list[VerifyPhoneRead]:
    """
    ! Get All Verify phones

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
        List of verify phone
    """
    # * Prepare filter fields
    filter_data.phone_number = (
        (VerifyPhone.phone_number.contains(filter_data.phone_number))
        if filter_data.phone_number
        else True
    )
    # * Add filter fields
    query = select(VerifyPhone).filter(
        and_(
            filter_data.phone_number,
        ),
    )
    obj_list = await verify_phone_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=VerifyPhoneRead)
async def read_permission(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_VERIFY_PHONE]),
    ),
    obj_data: IDRequest,
) -> VerifyPhoneRead:
    """
    ! Find Verify phone

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target VerifyPhone's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    VerifyPhoneNotFoundException
    """
    # * Verify location existence
    obj = await verify_phone_crud.verify_existence(db=db, verify_phone_id=obj_data.id)
    return obj
