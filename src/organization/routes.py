from random import randint
from typing import List, Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import and_, select, or_

from src import deps
from src.auth.exception import AccessDeniedException
from src.card.crud import CardValueType
from src.core.config import settings
from src.log.models import LogType
from src.organization.crud import organization as organization_crud
from src.location.crud import location as location_crud
from src.transaction.crud import transaction as transaction_crud
from src.agent.crud import agent as agent_crud
from src.organization.models import Organization
from src.organization.schema import (
    OrganizationRead,
    OrganizationFilter,
    OrganizationFilterOrderFild,
    OrganizationGenerateUser,
    OrganizationAppendUser,
    OrganizationPublicRead,
    OrganizationPublicResponse,
)
from src.schema import IDRequest, ResultResponse, UpdateActivityRequest
from src.transaction.models import (
    TransactionValueType,
    TransactionReasonEnum,
    TransactionStatusEnum,
)
from src.transaction.schema import TransactionCreate, TransactionRowCreate
from src.user.exception import UsernameIsDuplicatedException
from src.user.models import User
from src.permission import permission_codes as permission
from src.user.schema import UserRead, UserFilter, UserFilterOrderFild
from src.user.crud import user as user_crud
from src.log.crud import log as log_crud
from src.important_data.crud import important_data as important_data_crud
from src.auth.crud import auth as auth_crud
from src.card.crud import card as card_crud
from src.cash.crud import cash as cash_crud, CashField, TypeOperation
from src.user_message.models import UserMessage
from src.utils.file import read_excel_file
from src.utils.sms import send_welcome_sms
from src.wallet.exception import LackOfMoneyException

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
async def get_organization_list(
    *,
    db=Depends(deps.get_db),
    filter_data: OrganizationFilter,
    current_user: User = Depends(
        deps.get_current_user(),
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
    filter_data.name = (
        or_(
            User.first_name.contains(filter_data.name),
            User.last_name.contains(filter_data.name),
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
    filter_data.is_active = (
        (Organization.is_active == filter_data.is_active)
        if filter_data.is_active is not None
        else True
    )

    # * Add filter fields
    query = (
        select(Organization)
        .filter(
            and_(
                filter_data.is_active,
                filter_data.location_id,
                filter_data.user_id,
                filter_data.name,
                filter_data.location_id,
                filter_data.agent_id,
            ),
        )
        .join(Organization.user)
    ).order_by(Organization.created_at.desc())
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == OrganizationFilterOrderFild.is_active:
                query = query.order_by(Organization.is_active.desc())
            elif field == OrganizationFilterOrderFild.created_at:
                query = query.order_by(Organization.created_at.desc())
            elif field == OrganizationFilterOrderFild.updated_at:
                query = query.order_by(Organization.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == OrganizationFilterOrderFild.is_active:
                query = query.order_by(Organization.is_active.asc())
            elif field == OrganizationFilterOrderFild.created_at:
                query = query.order_by(Organization.created_at.asc())
            elif field == OrganizationFilterOrderFild.updated_at:
                query = query.order_by(Organization.updated_at.asc())
    # * Find All agent with filters
    obj_list = await organization_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list


# ---------------------------------------------------------------------------
@router.post(path="/list/public", response_model=OrganizationPublicResponse)
async def get_organization_public_list(
    *,
    db=Depends(deps.get_db),
    filter_data: OrganizationFilter,
    skip: int = 0,
    limit: int = 20,
) -> OrganizationPublicResponse:
    """
    ! Get All Organization

    Parameters
    ----------
    db
        Target database connection
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
    filter_data.name = (
        or_(
            User.first_name.contains(filter_data.name),
            User.last_name.contains(filter_data.name),
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
    filter_data.is_active = (
        (Organization.is_active == filter_data.is_active)
        if filter_data.is_active is not None
        else True
    )

    # * Add filter fields
    query = (
        select(Organization)
        .filter(
            and_(
                filter_data.is_active,
                filter_data.location_id,
                filter_data.user_id,
                filter_data.name,
                filter_data.location_id,
                filter_data.agent_id,
                Organization.is_active == True,
            ),
        )
        .join(Organization.user)
    ).order_by(Organization.created_at.desc())

    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == OrganizationFilterOrderFild.is_active:
                query = query.order_by(Organization.is_active.desc())
            elif field == OrganizationFilterOrderFild.created_at:
                query = query.order_by(Organization.created_at.desc())
            elif field == OrganizationFilterOrderFild.updated_at:
                query = query.order_by(Organization.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == OrganizationFilterOrderFild.is_active:
                query = query.order_by(Organization.is_active.asc())
            elif field == OrganizationFilterOrderFild.created_at:
                query = query.order_by(Organization.created_at.asc())
            elif field == OrganizationFilterOrderFild.updated_at:
                query = query.order_by(Organization.updated_at.asc())
    # * Find All agent with filters
    obj_list = await organization_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )

    count = await organization_crud.get_organization_users_count(
        db=db,
    )

    # ? Mapping
    res: list[OrganizationPublicRead] = []
    for org in obj_list:
        buf = OrganizationPublicRead(
            id=org.id,
            name=org.contract.position_request.name,
        )
        res.append(buf)

    return OrganizationPublicResponse(count=count, list=res)


# ---------------------------------------------------------------------------
@router.get("/me", response_model=OrganizationRead)
async def me(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> OrganizationRead:
    """
    ! Get My organization info

    Parameters
    ----------
    db
        database connection
    current_user
        requester user

    Returns
    -------
    response
        My organization data

    Raises
    ------
    OrganizationNotFoundException
    """
    organization = await organization_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )
    return organization


# ---------------------------------------------------------------------------
@router.post(path="/user/list", response_model=List[UserRead])
async def user_list(
    *,
    db=Depends(deps.get_db),
    filter_data: UserFilter,
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[UserRead]:
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
    organization = await organization_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )
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
    filter_data.name = (
        or_(
            User.first_name.contains(filter_data.name),
            User.last_name.contains(filter_data.name),
        )
        if filter_data.name is not None
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
                User.organization_id == organization.id,
                filter_data.name,
                filter_data.national_code,
                filter_data.phone_number,
                filter_data.is_active,
                filter_data.is_valid,
                filter_data.father_name,
                filter_data.tel,
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
    return obj_list


# ---------------------------------------------------------------------------
@router.post(path="/generate/user", response_model=ResultResponse)
async def generate_user(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    generate_data: OrganizationGenerateUser,
) -> ResultResponse:
    """
    ! Generate Organization User

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    generate_data
        Necessary data for generate new user for organization

    Returns
    -------
    res
        result of operation

    Raises
    ------
    AccessDeniedException
    UsernameIsDuplicatedException
    LocationNotFoundException
    OrganizationNotFoundException
    """
    # * Check requester role
    if not current_user.role.name == "سازمان":
        raise AccessDeniedException()

    organization_user = await organization_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    # * Check user not exist
    exist_user = await user_crud.check_by_username_and_national_code(
        db=db,
        username=generate_data.phone_number,
        national_code=generate_data.national_code,
    )
    if exist_user:
        raise UsernameIsDuplicatedException()

    # * Check location exist
    await location_crud.verify_existence(db=db, location_id=generate_data.location_id)

    # * Update Organization considered credit
    organization_user.total_considered_credit += generate_data.considered_credit
    db.add(organization_user)

    # ? Generate new User -> validation = False
    new_user = User(
        organization_id=organization_user.id,
        name=generate_data.name,
        last_name=generate_data.last_name,
        national_code=generate_data.national_code,
        phone_number=generate_data.phone_number,
        father_name=generate_data.father_name,
        birth_place=generate_data.birth_place,
        location_id=generate_data.location_id,
        postal_code=generate_data.postal_code,
        tel=generate_data.tel,
        address=generate_data.address,
        considered_credit=generate_data.considered_credit,
        personnel_number=generate_data.personnel_number,
        organizational_section=generate_data.organizational_section,
        job_class=generate_data.job_class,
    )
    new_user = await auth_crud.create_new_user(
        db=db,
        user=new_user,
    )

    # ? Create User Message
    user_message = UserMessage(
        title="خوش آمدید",
        text="{} عزیز ، عضویت شما را به خانواده آیکارت تبریک میگویم".format(
            new_user.first_name,
        ),
        user_id=new_user.id,
    )

    db.add(user_message)
    await db.commit()

    # * Send Register SMS
    send_welcome_sms(
        phone_number=generate_data.phone_number,
        full_name="{} {}".format(new_user.first_name, new_user.last_name),
    )

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.GENERATE_ORGANIZATION_USER,
        user_id=current_user.id,
        detail="کاربر {} با موفقیت توسط کاربر {} به عنوان کاربر سازمانی ایجاد شد".format(
            new_user.username,
            current_user.username,
        ),
    )

    return ResultResponse(result="User Created Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/append/user", response_model=ResultResponse)
async def append_user(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    append_data: OrganizationAppendUser,
) -> ResultResponse:
    """
    ! Append Organization User

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    append_data
        Necessary data for append user to organization

    Returns
    -------
    res
        result of operation

    Raises
    ------
    UserNotFoundException
    """
    # * Check requester role
    if not current_user.role.name == "سازمان":
        raise AccessDeniedException()

    organization_user = await organization_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    # * Check user not exist
    user = await user_crud.find_by_username_and_national_code(
        db=db,
        username=append_data.phone_number,
        national_code=append_data.national_code,
    )

    # * Update Organization considered credit
    organization_user.total_considered_credit += append_data.considered_credit
    db.add(organization_user)

    # ? Append new User
    user.organization_id = organization_user.id
    user.credit.considered = append_data.considered_credit

    db.add(user)
    await db.commit()

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.GENERATE_ORGANIZATION_USER,
        user_id=current_user.id,
        detail="کاربر {} با موفقیت توسط کاربر {} به سازمانی پیوست".format(
            user.username,
            current_user.username,
        ),
    )

    return ResultResponse(result="User Append Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/user/activation", response_model=ResultResponse)
async def user_activation(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    obj_id: IDRequest,
) -> ResultResponse:
    """
    ! Append Organization User

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_id
        User ID

    Returns
    -------
    res
        result of operation

    Raises
    ------
    UserNotFoundException
    AgentNotFoundException
    LackOfMoneyException
    """
    # * Check requester role
    if not current_user.role.name == "نماینده":
        raise AccessDeniedException()
    agent_user = await agent_crud.find_by_user_id(db=db, user_id=current_user.id)

    # * Check Agent cash
    cost = await important_data_crud.get_register_cost(db=db)
    if agent_user.user.cash.balance < cost:
        raise LackOfMoneyException()

    await cash_crud.update_cash_by_user(
        user=agent_user.user,
        cash_field=CashField.BALANCE,
        type_operation=TypeOperation.DECREASE,
        amount=cost,
    )

    # * Check user exist
    user = await user_crud.verify_existence(
        db=db,
        user_id=obj_id.id,
    )
    admin_user = await user_crud.verify_existence_by_username(
        db=db,
        username=settings.ADMIN_USERNAME,
    )

    transferor_card = await card_crud.get_active_card(
        db=db,
        card_value_type=CardValueType.CASH,
        wallet=user.wallet,
    )
    receiver_card = await card_crud.get_active_card(
        db=db,
        card_value_type=CardValueType.CASH,
        wallet=admin_user.wallet,
    )

    user.credit.active = True
    # ? Create Transaction
    transaction_create = TransactionCreate(
        status=TransactionStatusEnum.ACCEPTED,
        value=cost,
        text="پرداخت هزینه فعال سازی کاربر با کد ملی {}".format(user.national_code),
        value_type=TransactionValueType.CASH,
        receiver_id=receiver_card.id,
        transferor_id=transferor_card.id,
        code=await transaction_crud.generate_code(db=db),
        reason=TransactionReasonEnum.ORGANIZATION_REGISTER,
    )
    main_tr = await transaction_crud.create(db=db, obj_in=transaction_create)
    transaction_row_create = TransactionRowCreate(
        transaction_id=main_tr.id,
        status=main_tr.status,
        value=main_tr.value,
        text=main_tr.text,
        value_type=main_tr.value_type,
        receiver_id=main_tr.receiver_id,
        transferor_id=main_tr.transferor_id,
        code=await transaction_crud.generate_code(db=db),
        reason=main_tr.reason,
    )
    await transaction_crud.create(db=db, obj_in=transaction_row_create)

    db.add(agent_user)
    db.add(user)
    await db.commit()

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.ACTIVE_ORGANIZATION_USER,
        user_id=current_user.id,
        detail="کاربر سازمانی {} با موفقیت توسط کاربر {}  فعال شد".format(
            user.username,
            current_user.username,
        ),
    )

    return ResultResponse(result="User Append Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/upload/file", response_model=ResultResponse)
async def upload_file(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    image_file: Annotated[UploadFile, File()],
) -> ResultResponse:
    print(dir(image_file.file))
    await read_excel_file(db=db, user_id=current_user.id)
    return ResultResponse(result="User Append Successfully")


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
    ! Update Organization Activity

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update organization

    Returns
    -------
    obj
        Updated organization

    Raises
    ------
    UserNotFoundException
    """
    # * Verify user existence
    obj = await organization_crud.verify_existence(
        db=db,
        organization_id=update_data.where.id,
    )

    obj.is_active = update_data.data.is_active
    db.add(obj)
    await db.commit()

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.UPDATE_USER_ACTIVITY,
        detail="وضعیت سازمان {} با موفقیت توسط کاربر {} ویرایش شد".format(
            obj.contract.position_request.name,
            current_user.username,
        ),
    )

    return ResultResponse(result="Organization Activity Updated Successfully")
