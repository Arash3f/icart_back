from random import randint
from typing import List, Annotated

import pandas as pd
import os
from itertools import chain

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy import and_, select

from src import deps
from src.core.security import hash_password
from src.auth.exception import AccessDeniedException
from src.cash.models import Cash
from src.core.config import settings
from src.credit.models import Credit
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
)
from src.schema import IDRequest, ResultResponse
from src.transaction.models import TransactionValueType, TransactionReasonEnum
from src.transaction.schema import TransactionCreate
from src.user.exception import UsernameIsDuplicatedException
from src.user.models import User
from src.permission import permission_codes as permission
from src.user.schema import UserRead, UserFilter
from src.user.crud import user as user_crud
from src.user_message.models import UserMessage
from src.utils.file import read_excel_file
from src.utils.sms import send_welcome_sms
from src.wallet.exception import LackOfMoneyException
from src.wallet.models import Wallet

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


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[UserRead])
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
        else True
    )
    filter_data.phone_number = (
        (User.phone_number.contains(filter_data.phone_number))
        if filter_data.phone_number
        else True
    )

    # * Add filter fields
    query = select(User).filter(
        and_(
            User.organization_id == organization.id,
            filter_data.phone_number,
            filter_data.national_code,
        ),
    )
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

    # ? Create Credit
    credit = Credit(
        user=new_user,
        considered=generate_data.considered_credit,
    )

    # ? Create Cash
    cash = Cash(
        user=new_user,
    )

    # ? Create Wallet
    wallet_number = randint(100000, 999999)
    wallet = Wallet(
        user=new_user,
        number=wallet_number,
    )

    # ? Create User Message
    user_message = UserMessage(
        title="خوش آمدید",
        text="{} عزیز ، عضویت شما را به خانواده آیکارت تبریک میگویم".format(
            new_user.first_name,
        ),
        user_id=new_user.id,
    )

    db.add(new_user)
    db.add(credit)
    db.add(cash)
    db.add(wallet)
    db.add(user_message)
    await db.commit()
    # * Send Register SMS
    send_welcome_sms(
        phone_number=generate_data.phone_number,
        full_name="{} {}".format(new_user.first_name, new_user.last_name),
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
    if agent_user.user.cash.balance < 4900000:
        raise LackOfMoneyException()

    agent_user.user.cash.balance -= 4900000

    # * Check user exist
    user = await user_crud.verify_existence(
        db=db,
        user_id=obj_id.id,
    )

    icart_user = await user_crud.find_by_username(
        db=db,
        username=settings.ADMIN_USERNAME,
    )

    user.credit.active = True
    transaction = TransactionCreate(
        value=float(4900000),
        text="پرداخت هزینه فعال سازی کاربر با کد ملی {}".format(
            user.national_code),
        value_type=TransactionValueType.CASH,
        receiver_id=icart_user.wallet.id,
        transferor_id=agent_user.user.wallet.id,
        code=str(randint(100000000000, 999999999999)),
        reason=TransactionReasonEnum.REGISTER,
    )

    await transaction_crud.create(db=db, obj_in=transaction)

    db.add(agent_user)
    db.add(user)
    await db.commit()
    return ResultResponse(result="User Append Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/upload/file")
async def upload_file(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    excel_file: Annotated[UploadFile, File()]):
    result = dict()
    missing_data = list()
    invalid_username = list()
    invalid_location = list()
    duplicate_user = list()
    success_insert = list()
    
    # Get organization user
    # organization_user = await organization_crud.find_by_user_id(db=db,user_id=current_user.id)

    # Check file format
    file_format = os.path.splitext(excel_file.filename)[1]
    if file_format not in ['.xlsx', '.xls']:
        raise HTTPException(detail="فرمت فایل صحیح نمیباشد")

    excel_data = pd.read_excel(excel_file.file, index_col=0, header=1)

    col_dict = {'identity': ['نام', 'نام خانوادگی', 'کد ملی', 'شماره همراه', 'نام پدر', 'محل تولد'],
                'address': ['استان', 'شهر', 'کد پستی', 'شماره ثابت', 'آدرس'],
                'organization': ['شماره پرسنلی', 'بخش سازمان', 'طبقه شغلی'],
                'credit': ['میزان ریالی']}

    flatten_col = list(chain.from_iterable(col_dict.values()))
    if flatten_col.sort() != list(excel_data.columns).sort():
        raise HTTPException("فایل نامعتبر است")

    required_data = excel_data[chain.from_iterable([col_dict['identity'],col_dict['address'],col_dict['credit']])]

    has_null_data = excel_data[required_data.isna().any(axis=1)]
    missing_data.append(f'کاربران ردیف {has_null_data.index.values} دارای اطلاعات ناقص هستند')
    valid_data = excel_data[~required_data.isna().any(axis=1)]

    for index,row in valid_data.iterrows():
        # Apply inser user
        if len(str(row['شماره همراه'])) != 11:
            invalid_username.append(f'کاربر ردیف {index} به دلیل نامعتبر بودن شماره تلفن ثبت نشد')

        else:
            # ! find location
            location = await location_crud.find_by_name(db=db, name=row['شهر'])

            if not location:
                invalid_location.append(f'کاربر ردیف {index} به دلیل پیدا نشدن شهر ثبت نشد')
            else:
                # * Check user not exist
                exist_user = await user_crud.check_by_username_and_national_code(
                    db=db,
                    username=str(row['شماره همراه']),
                    national_code=str(row['کد ملی']),
                )
                if exist_user:
                    if exist_user.credit.considered:
                        pass
                        # current_user.total_considered_credit -= (
                        #     exist_user.credit.considered
                        # )
                    # current_user.total_considered_credit += int(row[15].value)
                    # db.add(current_user)

                    # ? Append new User
                    # exist_user.organization_id = current_user.id
                    # exist_user.credit.considered = int(row[15].value)
                else:
                    # * Update Organization considered credit
                    # current_user.total_considered_credit += int(row[15].value)
                    # db.add(current_user)
                    pass

                    find_user = await user_crud.check_by_username_or_national_code(
                        db=db,
                        username=str(row['شماره همراه']),
                        national_code=str(row['کد ملی']),
                    )
                    if find_user:
                        duplicate_user.append(f'کاربر ردیف {index} به دلیل تکراری بودن شماره همراه یا کد ملی ثبت نشد')
                    else:
                        # ? Generate new User -> validation = False
                        new_user = User(
                            organization_id=current_user.id,
                            first_name=row['نام'],
                            last_name=row['نام خانوادگی'],
                            national_code=str(row['کد ملی']),
                            phone_number=str(row['شماره همراه']),
                            father_name=row['نام پدر'],
                            birth_place=row['محل تولد'],
                            location_id=location.id,
                            postal_code=str(row['کد پستی']),
                            tel=str(row['شماره ثابت']),
                            address=row['آدرس'],
                            personnel_number=str(row['شماره پرسنلی']),
                            organizational_section=row['بخش سازمان'],
                            job_class=row['طبقه شغلی'],
                            password=hash_password(str(123456789)),
                        )

                        # ? Create Credit
                        credit = Credit(
                            user=new_user,
                            considered=int(row['میزان ریالی']),
                        )

                        # ? Create Cash
                        cash = Cash(
                            user=new_user,
                        )

                        # ? Create Wallet
                        wallet_number = randint(100000, 999999)
                        wallet = Wallet(
                            user=new_user,
                            number=wallet_number,
                        )

                        db.add(new_user)
                        db.add(credit)
                        db.add(cash)
                        db.add(wallet)

                        await db.commit()
                        success_insert.append(f'کاربر ردیف {index} با موفقیت ثبت شد')
    result.update({'missing data': missing_data,
                   'invalid username':invalid_username,
                   'invalid location':invalid_location,
                   'duplicate user':duplicate_user,
                   'success insert':success_insert})
    return result
