from fastapi import APIRouter, Depends, UploadFile, File
from jdatetime import timedelta
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.auth.exception import AccessDeniedException
from src.card.crud import CardValueType
from src.card.schema import ReferralCode
from src.cash.crud import CashField, TypeOperation
from src.core.config import settings
from src.log.models import LogType
from src.organization.models import Organization
from src.role.exception import CanNotChantUserWithMainRole
from src.schema import ResultResponse, ChartResponse, ChartFilterInput, Duration
from src.transaction.models import (
    TransactionValueType,
    TransactionStatusEnum,
    TransactionReasonEnum,
)
from src.transaction.schema import TransactionRowCreate, TransactionCreate
from src.user.models import User
from src.user.schema import (
    UserMeResponse,
    UserRead,
    UserFilter,
    UpdateUserRequest,
    UserRead2,
    UpdateUserActivityRequest,
    UserFilterOrderFild,
    UserRoleUpdate,
    UserReadV2,
)
from src.utils.minio_client import MinioClient
from typing import Annotated, List
from src.user.crud import user as user_crud
from src.organization.crud import organization as organization_crud
from src.role.crud import role as role_crud
from src.transaction.crud import transaction as transaction_crud
from src.cash.crud import cash as cash_crud
from src.card.crud import card as card_crud
from src.transaction.crud import transaction_row as transaction_row_crud
from src.important_data.crud import important_data as important_data_crud
from src.location.crud import location as location_crud
from src.log.crud import log as log_crud
from src.permission import permission_codes as permission

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/user", tags=["user"])


# ---------------------------------------------------------------------------
@router.get("/me", response_model=UserMeResponse)
async def me(
    current_user: User = Depends(deps.get_current_user_v2()),
) -> UserMeResponse:
    """
    ! Get My data

    Parameters
    ----------
    current_user
        Requester User

    Returns
    -------
    user
        Requester User data

    """
    user = current_user
    return user


# ---------------------------------------------------------------------------
@router.post(path="/update/image", response_model=ResultResponse)
async def update_image(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    image_file: Annotated[UploadFile, File()],
    current_user: User = Depends(
        deps.get_current_user(),
    ),
) -> ResultResponse:
    """
    ! Update user image

    Parameters
    ----------
    db
    minio
    current_user
    image_file

    Returns
    -------
    response
        Result of operation
    """
    # * Remove old image
    if current_user.image_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=current_user.image_name,
            version_id=current_user.image_version_id,
        )

    # * Save Contract File
    image_file = minio.client.put_object(
        data=image_file.file,
        object_name=image_file.filename,
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    current_user.image_version_id = image_file.version_id
    current_user.image_name = image_file.object_name

    db.add(current_user)
    await db.commit()
    return ResultResponse(result="Image Updated Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/update/background/image", response_model=ResultResponse)
async def update_background_image(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    image_file: Annotated[UploadFile, File()],
    current_user: User = Depends(
        deps.get_current_user(),
    ),
) -> ResultResponse:
    """
    ! Update user image

    Parameters
    ----------
    db
    minio
    current_user
    image_file

    Returns
    -------
    response
        Result of operation
    """
    # * Remove old image
    if current_user.image_background_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=current_user.image_background_name,
            version_id=current_user.image_background_version_id,
        )

    # * Save Contract File
    image_file = minio.client.put_object(
        data=image_file.file,
        object_name=image_file.filename,
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    current_user.image_background_version_id = image_file.version_id
    current_user.image_background_name = image_file.object_name

    db.add(current_user)
    await db.commit()
    return ResultResponse(result="Image Updated Successfully")


@router.delete(path="/image/delete", response_model=ResultResponse)
async def delete_image_file(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    current_user: User = Depends(deps.get_current_user()),
) -> ResultResponse:
    """
    ! Delete User Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    current_user
        Requester User

    Returns
    -------
    res
        result of operation
    """
    if current_user.image_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=current_user.image_name,
            version_id=current_user.image_version_id,
        )
        current_user.image_name = None
        current_user.image_version_id = None
        db.add(current_user)
        await db.commit()

    return ResultResponse(result="Image Deleted Successfully")


@router.delete(path="/background/delete", response_model=ResultResponse)
async def get_background_file(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    current_user: User = Depends(deps.get_current_user()),
) -> ResultResponse:
    """
    ! Delete User Background Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    current_user
        Requester User

    Returns
    -------
    res
        result of operation
    """
    if current_user.image_background_version_id:
        minio.client.get_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=current_user.image_background_name,
            version_id=current_user.image_background_version_id,
        )
        current_user.image_background_name = None
        current_user.image_background_version_id = None
        db.add(current_user)
        await db.commit()

    return ResultResponse(result="Image Deleted Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[UserRead2])
async def user_list(
    *,
    db=Depends(deps.get_db),
    filter_data: UserFilter,
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_USER]),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[UserRead2]:
    """
    ! Get All User

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
        List of user
    """
    # * Prepare filter fields
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code
        else True is not None
    )
    filter_data.phone_number = (
        (User.phone_number.contains(filter_data.phone_number))
        if filter_data.phone_number is not None
        else True
    )
    filter_data.location_id = (
        (User.location_id == filter_data.location_id)
        if filter_data.location_id
        else True is not None
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
    filter_data.is_active = (
        (User.is_active == filter_data.is_active)
        if filter_data.is_active is not None
        else True
    )
    filter_data.is_valid = (
        (User.is_active == filter_data.is_valid)
        if filter_data.is_valid is not None
        else True
    )
    filter_data.father_name = (
        (User.father_name.contains(filter_data.father_name))
        if filter_data.father_name is not None
        else True
    )
    filter_data.tel = (
        (User.father_name.contains(filter_data.tel))
        if filter_data.tel is not None
        else True
    )

    # * Add filter fields
    query = (
        select(User)
        .filter(
            and_(
                filter_data.name,
                filter_data.last_name,
                filter_data.national_code,
                filter_data.phone_number,
                filter_data.is_active,
                filter_data.is_valid,
                filter_data.father_name,
                filter_data.tel,
                filter_data.location_id,
            ),
        )
        .order_by(User.created_at.desc())
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == UserFilterOrderFild.national_code:
                query = query.order_by(User.national_code.desc())
            elif field == UserFilterOrderFild.phone_number:
                query = query.order_by(User.phone_number.desc())
            elif field == UserFilterOrderFild.first_name:
                query = query.order_by(User.first_name.desc())
            elif field == UserFilterOrderFild.last_name:
                query = query.order_by(User.last_name.desc())
            elif field == UserFilterOrderFild.is_active:
                query = query.order_by(User.is_active.desc())
            elif field == UserFilterOrderFild.is_valid:
                query = query.order_by(User.is_valid.desc())
            elif field == UserFilterOrderFild.created_at:
                query = query.order_by(User.created_at.desc())
            elif field == UserFilterOrderFild.updated_at:
                query = query.order_by(User.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == UserFilterOrderFild.national_code:
                query = query.order_by(User.national_code.asc())
            elif field == UserFilterOrderFild.phone_number:
                query = query.order_by(User.phone_number.asc())
            elif field == UserFilterOrderFild.first_name:
                query = query.order_by(User.first_name.asc())
            elif field == UserFilterOrderFild.last_name:
                query = query.order_by(User.last_name.asc())
            elif field == UserFilterOrderFild.is_active:
                query = query.order_by(User.is_active.asc())
            elif field == UserFilterOrderFild.is_valid:
                query = query.order_by(User.is_valid.asc())
            elif field == UserFilterOrderFild.created_at:
                query = query.order_by(User.created_at.asc())
            elif field == UserFilterOrderFild.updated_at:
                query = query.order_by(User.updated_at.asc())
    # * Find All agent with filters
    obj_list = await user_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    for i in obj_list:
        if i.location:
            loc = await location_crud.verify_existence(
                db=db,
                location_id=i.location.parent_id,
            )
            i.location.parent = loc
    return obj_list


# ---------------------------------------------------------------------------
@router.post("/my/referrer", response_model=list[UserReadV2])
async def my_referrer(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    skip: int = 0,
    limit: int = 10,
) -> list[UserReadV2]:
    query = (
        select(User)
        .filter(
            User.referrer_id == current_user.id,
        )
        .order_by(User.created_at.desc())
    )
    obj_list = await user_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list


# ---------------------------------------------------------------------------
@router.post("/verify/referral_code", response_model=ResultResponse)
async def verify_referral_code(
    *,
    db: AsyncSession = Depends(deps.get_db),
    data: ReferralCode,
    current_user: User = Depends(
        deps.get_current_user_v3(),
    ),
) -> ResultResponse:
    await user_crud.verify_existence_by_referral_code(
        db=db,
        referral_code=data.referral_code,
    )

    if not current_user.referrer_id:
        admin_user = await user_crud.verify_existence_by_username(
            db=db,
            username=settings.ADMIN_USERNAME,
        )
        admin_card = await card_crud.get_active_card(
            db=db,
            card_value_type=CardValueType.CASH,
            wallet=admin_user.wallet,
        )
        important_data = await important_data_crud.get_last_obj(db=db)
        referrer_user = await user_crud.find_by_referral_code(
            db=db,
            referral_code=data.referral_code,
        )
        referrer_user_card = await card_crud.get_active_card(
            db=db,
            card_value_type=CardValueType.CASH,
            wallet=referrer_user.wallet,
        )
        # ? Generate transaction
        transaction = TransactionCreate(
            value=important_data.referral_reward,
            text=" سود خرید کارت بلو با کد معرف",
            value_type=TransactionValueType.CASH,
            receiver_id=referrer_user_card.id,
            transferor_id=admin_card.id,
            code=await transaction_crud.generate_code(db=db),
            status=TransactionStatusEnum.ACCEPTED,
            reason=TransactionReasonEnum.PROFIT,
        )
        main_tr = await transaction_crud.create(db=db, obj_in=transaction)
        referrer_transaction = TransactionRowCreate(
            transaction_id=main_tr.id,
            value=important_data.referral_reward,
            text=" سود خرید کارت بلو با کد معرف",
            value_type=TransactionValueType.CASH,
            receiver_id=referrer_user_card.id,
            transferor_id=admin_card.id,
            code=await transaction_row_crud.generate_code(db=db),
            status=TransactionStatusEnum.ACCEPTED,
            reason=TransactionReasonEnum.PROFIT,
        )
        await transaction_row_crud.create(db=db, obj_in=referrer_transaction)
        await cash_crud.update_cash_by_user(
            db=db,
            user=referrer_user,
            amount=important_data.referral_reward,
            cash_field=CashField.CASH_BACK,
            type_operation=TypeOperation.INCREASE,
        )

        current_user.referrer_id = referrer_user.id
        db.add(current_user)
        await db.commit()
    return ResultResponse(result="Success")


# ---------------------------------------------------------------------------
@router.put(path="/update", response_model=UserRead)
async def update_user(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_USER]),
    ),
    update_data: UpdateUserRequest,
) -> UserRead:
    """
    ! Update User

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update user

    Returns
    -------
    obj
        Updated user

    Raises
    ------
    LocationNotFoundException
    UserNotFoundException
    """
    # * Verify user existence
    obj_current = await user_crud.verify_existence(
        db=db,
        user_id=update_data.where.id,
    )

    # * Verify location existence
    if update_data.data.location_id:
        await location_crud.verify_existence(
            db=db,
            location_id=update_data.data.parent_id,
        )

    obj = await location_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.UPDATE_USER,
        detail="کاربر {} با موفقیت توسط کاربر {} ویرایش شد".format(
            obj.username,
            current_user.username,
        ),
    )

    return obj


# ---------------------------------------------------------------------------
@router.put(path="/update/activity", response_model=UserRead)
async def update_user_activity(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CHANGE_USER_ACTIVITY]),
    ),
    update_data: UpdateUserActivityRequest,
) -> UserRead:
    """
    ! Update User Activity

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update user

    Returns
    -------
    obj
        Updated user

    Raises
    ------
    UserNotFoundException
    """
    # * Verify user existence
    obj = await user_crud.verify_existence(
        db=db,
        user_id=update_data.where.id,
    )

    obj.is_active = update_data.data.is_active
    db.add(obj)
    await db.commit()

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.UPDATE_USER_ACTIVITY,
        detail="وضعیت کاربر {} با موفقیت توسط کاربر {} ویرایش شد".format(
            obj.username,
            current_user.username,
        ),
    )

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/organization/list", response_model=List[UserRead2])
async def organization_user_list(
    *,
    db=Depends(deps.get_db),
    filter_data: UserFilter,
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[UserRead2]:
    """
    ! Get All Organization User

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
        List of user

    Raises
    ------
    AccessDeniedException
    """
    if current_user.role.name != "سازمان":
        raise AccessDeniedException()

    organization_user = await organization_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    # * Prepare filter fields
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code
        else True is not None
    )
    filter_data.location_id = (
        (User.location_id == filter_data.location_id)
        if filter_data.location_id
        else True is not None
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
    filter_data.is_active = (
        (User.is_active == filter_data.is_active)
        if filter_data.is_active is not None
        else True
    )
    filter_data.is_valid = (
        (User.is_active == filter_data.is_valid)
        if filter_data.is_valid is not None
        else True
    )
    filter_data.father_name = (
        (User.father_name.contains(filter_data.father_name))
        if filter_data.father_name is not None
        else True
    )
    filter_data.tel = (
        (User.father_name.contains(filter_data.tel))
        if filter_data.tel is not None
        else True
    )

    # * Add filter fields
    query = (
        select(User)
        .filter(
            and_(
                filter_data.name,
                filter_data.last_name,
                filter_data.national_code,
                filter_data.phone_number,
                filter_data.is_active,
                filter_data.is_valid,
                filter_data.father_name,
                filter_data.tel,
                filter_data.location_id,
                User.organization_id == organization_user.id,
            ),
        )
        .order_by(User.created_at.desc())
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == UserFilterOrderFild.national_code:
                query = query.order_by(User.national_code.desc())
            elif field == UserFilterOrderFild.phone_number:
                query = query.order_by(User.phone_number.desc())
            elif field == UserFilterOrderFild.first_name:
                query = query.order_by(User.first_name.desc())
            elif field == UserFilterOrderFild.last_name:
                query = query.order_by(User.last_name.desc())
            elif field == UserFilterOrderFild.is_active:
                query = query.order_by(User.is_active.desc())
            elif field == UserFilterOrderFild.is_valid:
                query = query.order_by(User.is_valid.desc())
            elif field == UserFilterOrderFild.created_at:
                query = query.order_by(User.created_at.desc())
            elif field == UserFilterOrderFild.updated_at:
                query = query.order_by(User.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == UserFilterOrderFild.national_code:
                query = query.order_by(User.national_code.asc())
            elif field == UserFilterOrderFild.phone_number:
                query = query.order_by(User.phone_number.asc())
            elif field == UserFilterOrderFild.first_name:
                query = query.order_by(User.first_name.asc())
            elif field == UserFilterOrderFild.last_name:
                query = query.order_by(User.last_name.asc())
            elif field == UserFilterOrderFild.is_active:
                query = query.order_by(User.is_active.asc())
            elif field == UserFilterOrderFild.is_valid:
                query = query.order_by(User.is_valid.asc())
            elif field == UserFilterOrderFild.created_at:
                query = query.order_by(User.created_at.asc())
            elif field == UserFilterOrderFild.updated_at:
                query = query.order_by(User.updated_at.asc())
    # * Find All agent with filters
    obj_list = await user_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    for i in obj_list:
        if i.location:
            loc = await location_crud.verify_existence(
                db=db,
                location_id=i.location.parent_id,
            )
            i.location.parent = loc
    return obj_list


# ---------------------------------------------------------------------------
@router.post(path="/agent/list", response_model=List[UserRead2])
async def agent_list(
    *,
    db=Depends(deps.get_db),
    filter_data: UserFilter,
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[UserRead2]:
    """
    ! Get All Agent User

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
        List of user

    Raises
    ------
    AccessDeniedException
    """
    if current_user.role.name != "نماینده":
        raise AccessDeniedException()

    agent_user = await organization_crud.find_by_user_id(db=db, user_id=current_user.id)

    organization_user = await organization_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    # * Prepare filter fields
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code
        else True is not None
    )
    filter_data.location_id = (
        (User.location_id == filter_data.location_id)
        if filter_data.location_id
        else True is not None
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
    filter_data.is_active = (
        (User.is_active == filter_data.is_active)
        if filter_data.is_active is not None
        else True
    )
    filter_data.is_valid = (
        (User.is_active == filter_data.is_valid)
        if filter_data.is_valid is not None
        else True
    )
    filter_data.father_name = (
        (User.father_name.contains(filter_data.father_name))
        if filter_data.father_name is not None
        else True
    )
    filter_data.tel = (
        (User.father_name.contains(filter_data.tel))
        if filter_data.tel is not None
        else True
    )

    # * Add filter fields
    query = (
        select(User)
        .filter(
            and_(
                filter_data.name,
                filter_data.last_name,
                filter_data.national_code,
                filter_data.phone_number,
                filter_data.is_active,
                filter_data.is_valid,
                filter_data.father_name,
                filter_data.tel,
                filter_data.location_id,
            ),
            or_(
                Organization.agent_id == agent_user.id,
                User.agent_id == agent_user.id,
            ),
        )
        .join(User.organization)
        .order_by(User.created_at.desc())
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == UserFilterOrderFild.national_code:
                query = query.order_by(User.national_code.desc())
            elif field == UserFilterOrderFild.phone_number:
                query = query.order_by(User.phone_number.desc())
            elif field == UserFilterOrderFild.first_name:
                query = query.order_by(User.first_name.desc())
            elif field == UserFilterOrderFild.last_name:
                query = query.order_by(User.last_name.desc())
            elif field == UserFilterOrderFild.is_active:
                query = query.order_by(User.is_active.desc())
            elif field == UserFilterOrderFild.is_valid:
                query = query.order_by(User.is_valid.desc())
            elif field == UserFilterOrderFild.created_at:
                query = query.order_by(User.created_at.desc())
            elif field == UserFilterOrderFild.updated_at:
                query = query.order_by(User.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == UserFilterOrderFild.national_code:
                query = query.order_by(User.national_code.asc())
            elif field == UserFilterOrderFild.phone_number:
                query = query.order_by(User.phone_number.asc())
            elif field == UserFilterOrderFild.first_name:
                query = query.order_by(User.first_name.asc())
            elif field == UserFilterOrderFild.last_name:
                query = query.order_by(User.last_name.asc())
            elif field == UserFilterOrderFild.is_active:
                query = query.order_by(User.is_active.asc())
            elif field == UserFilterOrderFild.is_valid:
                query = query.order_by(User.is_valid.asc())
            elif field == UserFilterOrderFild.created_at:
                query = query.order_by(User.created_at.asc())
            elif field == UserFilterOrderFild.updated_at:
                query = query.order_by(User.updated_at.asc())
    # * Find All agent with filters
    obj_list = await user_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    for i in obj_list:
        if i.location:
            loc = await location_crud.verify_existence(
                db=db,
                location_id=i.location.parent_id,
            )
            i.location.parent = loc
    return obj_list


# ---------------------------------------------------------------------------
@router.post(path="/acquisition/statistics", response_model=List[ChartResponse])
async def acquisition_statistics(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_USER]),
    ),
    filter_data: ChartFilterInput,
) -> list[ChartResponse]:
    """
    ! Get user acquisition statistics

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user
    filter_data
        filter data

    Returns
    -------
    chart_data
        chart final data
    """
    start = filter_data.duration.start_date
    end = filter_data.duration.end_date
    unit = filter_data.unit

    chart_data: list[ChartResponse] = []

    # ? calculate durations
    buf_time = start
    while buf_time < end:
        buf_end = buf_time + timedelta(
            days=unit,
        )
        duration = Duration(
            start_date=buf_time,
            end_date=buf_end,
        )
        obj = ChartResponse(
            duration=duration,
            value=0,
        )

        query = (
            select(func.count())
            .select_from(User)
            .filter(
                and_(
                    User.created_at >= obj.duration.start_date,
                    User.created_at < obj.duration.end_date,
                ),
            )
        )
        response = await db.execute(
            query,
        )
        obj.value = response.scalar()

        chart_data.append(obj)
        buf_time = buf_end

    return chart_data


# ---------------------------------------------------------------------------
@router.put("/update/role", response_model=ResultResponse)
async def update_user_role(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_ROLE]),
    ),
    update_data: UserRoleUpdate,
) -> ResultResponse:
    """
    ! Update User Role

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update role

    Returns
    -------
    role
        Updated role

    Raises
    ------
    RoleNotFoundException
    RoleNameIsDuplicatedException
    """
    user = await user_crud.verify_existence(
        db=db,
        user_id=update_data.where.id,
    )

    if (
        user.role.name == "نماینده"
        or user.role.name == "پذیرنده"
        or user.role.name == "سازمان"
    ):
        raise CanNotChantUserWithMainRole()

    # * Verify role's name duplicate
    role = await role_crud.verify_existence(
        db=db,
        role_id=update_data.data.role_id,
    )

    user.role = role

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.UPDATE_ROLE,
        detail="نقش کاربر {} با موفقیت توسط کاربر {} ویرایش شد".format(
            user.username,
            current_user.national_code,
        ),
    )

    return ResultResponse(result="User Role Updated Successfully")
