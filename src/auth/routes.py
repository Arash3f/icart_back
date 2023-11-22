from datetime import datetime, timedelta
from random import randint

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pytz import timezone
from sqlalchemy.ext.asyncio import AsyncSession
from src.permission import permission_codes as permission

from src import deps
from src.auth.crud import auth as auth_crud
from src.auth.exception import (
    InactiveUserException,
    IncorrectUsernameOrPasswordException,
    IncorrectVerifyCodeException,
)
from src.auth.schema import (
    ForgetPasswordIn,
    OneTimePasswordRequestIn,
    UserRegisterIn,
    VerifyUsernameAndNationalCode,
    UpdateUserValidationRequest,
    LoginResponse,
)
from src.core.config import settings
from src.core.security import hash_password
from src.role.crud import role as role_crud
from src.schema import ResultResponse, IDRequest
from src.user.crud import user as user_crud
from src.user.models import User
from src.user.schema import UserRead
from src.user_message.models import UserMessage
from src.utils.sms import send_one_time_password_sms, send_welcome_sms
from src.verify_phone.crud import verify_phone as verify_phone_crud

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
@router.post("/login")
async def login(
    *,
    db: AsyncSession = Depends(deps.get_db),
    login_form: OAuth2PasswordRequestForm = Depends(),
) -> LoginResponse:
    """
    ! Normal Login

    Parameters
    ----------
    db
        Target database connection
    login_form
        Necessary data for login

    Returns
    -------
    access_token
        User access token

    Raises
    ------
    IncorrectUsernameOrPasswordException
    InactiveUserException
    """
    user = await auth_crud.authenticate(
        db=db,
        username=login_form.username,
        password=login_form.password,
    )
    if not user:
        raise IncorrectUsernameOrPasswordException()
    elif not user.is_active:
        raise InactiveUserException()
    # * Generate Access Token
    access_token = await auth_crud.generate_access_token(user=user)
    res = LoginResponse(
        token=access_token,
        role_name=user.role.name,
        is_valid=user.is_valid,
    )
    return res


# ---------------------------------------------------------------------------
@router.post("/login_from_admin")
async def login_from_admin(
    *,
    db: AsyncSession = Depends(deps.get_db),
    data_in: IDRequest,
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.LOGIN_AS_ADMIN]),
    ),
) -> LoginResponse:
    """
    ! Normal Login

    Parameters
    ----------
    db
        Target database connection
    current_user
        user have permission

    Returns
    -------
    access_token
        User access token

    Raises
    ------
    UserNotFoundException
    """
    user = await user_crud.verify_existence(db=db, user_id=data_in.id)
    # * Generate Access Token
    access_token = await auth_crud.generate_access_token(user=user)
    res = LoginResponse(
        token=access_token,
        role_name=user.role,
        is_valid=user.is_valid,
    )
    return res


@router.post("/login/one_time_password")
async def login_one_time_password(
    *,
    db: AsyncSession = Depends(deps.get_db),
    login_form: OAuth2PasswordRequestForm = Depends(),
) -> LoginResponse:
    """
    ! Login with one time password

    Parameters
    ----------
    db
        Target database connection
    login_form
        Necessary data for login

    Returns
    -------
    access_token
        User access token

    Raises
    ------
    IncorrectUsernameOrPasswordException
        Username Or Password Is Incorrect
    InactiveUserException
        User Is Inactive
    """
    current_time = datetime.now(timezone("Asia/Tehran"))

    user = await auth_crud.authenticate_by_one_time_password(
        db=db,
        username=login_form.username,
        password=login_form.password,
    )
    if not user or user.expiration_password_at < current_time:
        raise IncorrectUsernameOrPasswordException()
    elif not user.is_active:
        raise InactiveUserException()
    # * Generate Access Token
    access_token = await auth_crud.generate_access_token(user=user)

    res = LoginResponse(
        token=access_token,
        role_name=user.role.name,
        is_valid=user.is_valid,
    )
    return res


# ---------------------------------------------------------------------------
@router.post(
    "/one_time_password/request",
    response_model=ResultResponse,
    status_code=200,
)
async def request_one_time_password(
    *,
    db: AsyncSession = Depends(deps.get_db),
    request_data: OneTimePasswordRequestIn,
) -> ResultResponse:
    """
    ! Request for one time password

    Parameters
    ----------
    db
        Target database connection
    request_data
        User's username

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    UserNotFoundException
    """
    one_time_password = randint(100000, 999999)
    # * Find user
    user = await user_crud.verify_existence_by_username(
        db=db,
        username=request_data.username,
    )
    # * Update user data
    user.one_time_password = hash_password(str(one_time_password))
    user.expiration_password_at = datetime.now(timezone("Asia/Tehran")) + timedelta(
        minutes=settings.DYNAMIC_PASSWORD_EXPIRE_MINUTES,
    )

    # todo: SMS Send SMS to user's phone
    send_one_time_password_sms(
        phone_number=user.phone_number,
        one_time_password=str(one_time_password),
        exp_time=user.expiration_password_at,
    )

    db.add(user)
    await db.commit()
    return ResultResponse(result="Code sent successfully")


# ---------------------------------------------------------------------------
@router.post("/verify/register/data", response_model=ResultResponse, status_code=200)
async def verify_register_data(
    *,
    db: AsyncSession = Depends(deps.get_db),
    request_data: VerifyUsernameAndNationalCode,
) -> ResultResponse:
    """
    ! Verify register data [phone number, national code]

    Parameters
    ----------
    db
        Target database connection
    request_data
        phone number, national code

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    UsernameIsDuplicatedException
    """
    # todo: Verify verify phone number and national code with web server

    await user_crud.verify_not_existence_by_username_and_national_code(
        db=db,
        username=request_data.username,
        national_code=request_data.national_code,
    )

    return ResultResponse(result="User not exist")


# ---------------------------------------------------------------------------
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ResultResponse,
)
async def register(
    *,
    db: AsyncSession = Depends(deps.get_db),
    register_data: UserRegisterIn,
) -> ResultResponse:
    """
    ! Register User

    Parameters
    ----------
    db
        Target database connection
    register_data
        Necessary data for Create user

    Returns
    -------
    created_user
        New User

    Raises
    ------
    RoleNotFoundException
        It does not normally happen
    IncorrectVerifyCodeException
    UsernameIsDuplicatedException
    """
    phone_number = register_data.phone_number
    verify_code = register_data.phone_verify_code
    current_time = datetime.now(timezone("Asia/Tehran"))
    role = await role_crud.verify_existence_by_name(db=db, name="کاربر ساده")

    # todo: Verify phone number and national code with web server

    # ? Verify Phone Number
    verify_code_number = await verify_phone_crud.find_by_phone_number(
        db=db,
        phone_number=phone_number,
    )
    # ? Verify phone number code
    if (
        not verify_code_number
        or verify_code_number.verify_code != verify_code
        or verify_code_number.expiration_code_at < current_time
    ):
        raise IncorrectVerifyCodeException()
    # ? Verify duplicate username
    await user_crud.verify_duplicate_username(db=db, username=phone_number)
    # ? Verify duplicate national_code
    await user_crud.verify_duplicate_national_code(
        db=db,
        national_code=register_data.national_code,
    )

    # ? Create User
    created_user = User(
        username=phone_number,
        password=hash_password(register_data.password),
        role_id=role.id,
        first_name=register_data.first_name,
        last_name=register_data.last_name,
        national_code=register_data.national_code,
        phone_number=phone_number,
    )
    user = await auth_crud.create_new_user(db=db, user=created_user)

    # ? Create User Message
    user_message = UserMessage(
        title="خوش آمدید",
        text="{} عزیز ، عضویت شما را به خانواده آیکارت تبریک میگویم".format(
            user.first_name,
        ),
        user_id=user.id,
    )

    # * Send Register SMS
    send_welcome_sms(
        phone_number=phone_number,
        full_name="{} {}".format(created_user.first_name, created_user.last_name),
    )

    db.add(user_message)
    await db.commit()

    return ResultResponse(result="User Created Successfully")


# ---------------------------------------------------------------------------
@router.post("/forget/password", response_model=ResultResponse, status_code=200)
async def forget_password(
    *,
    db: AsyncSession = Depends(deps.get_db),
    request_data: ForgetPasswordIn,
) -> ResultResponse:
    user = await user_crud.find_by_username_and_national_code(
        db=db,
        username=request_data.phone_number,
        national_code=request_data.national_code,
    )

    verify_phone_crud.verify_with_verify_code(
        db=db,
        phone_number=request_data.phone_number,
        verify_code=request_data.code,
    )

    user.password = hash_password(request_data.password)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return ResultResponse(result="password updated successfully")


# ---------------------------------------------------------------------------
@router.put(path="/update/validation", response_model=UserRead)
async def update_user_activity(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_USER]),
    ),
    update_data: UpdateUserValidationRequest,
) -> UserRead:
    """
    ! Update User Validation

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

    obj.is_valid = update_data.data.is_valid
    db.add(obj)
    await db.commit()
    return obj
