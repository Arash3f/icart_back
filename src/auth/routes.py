from datetime import datetime, timedelta, timezone
from random import randint

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.auth.crud import auth as auth_crud
from src.auth.exception import (
    InactiveUserException,
    IncorrectUsernameOrPasswordException,
    IncorrectVerifyCodeException,
)
from src.auth.schema import (
    AccessToken,
    ForgetPasswordIn,
    OneTimePasswordRequestIn,
    UserRegisterIn,
    VerifyUsernameAndNationalCode,
)
from src.core.config import settings
from src.core.security import hash_password
from src.credit.models import Credit
from src.role.crud import role as role_crud
from src.schema import ResultResponse
from src.user.crud import user as user_crud
from src.user.models import User
from src.utils.sms import send_one_time_password_sms, send_welcome_sms
from src.verify_phone.crud import verify_phone as verify_phone_crud
from src.wallet.models import Wallet

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
@router.post("/login")
async def login(
    *,
    db: AsyncSession = Depends(deps.get_db),
    login_form: OAuth2PasswordRequestForm = Depends(),
) -> AccessToken:
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
        Username Or Password Is Incorrect
    InactiveUserException
        User Is Inactive

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
    return access_token


@router.post("/login/one_time_password")
async def login_one_time_password(
    *,
    db: AsyncSession = Depends(deps.get_db),
    login_form: OAuth2PasswordRequestForm = Depends(),
) -> AccessToken:
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
    current_time = datetime.now(tz=timezone.utc)

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
    return access_token


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
    db.add(user)
    await db.commit()
    # ? Send SMS to user's phone
    send_one_time_password_sms(
        phone_number=user.phone_number,
        one_time_password=str(one_time_password),
        exp_time=user.expiration_password_at,
    )
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
    # todo: verify phone number and national code with web server

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

    # todo: verify phone number and national code with web server

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

    # ? Create Credit
    credit = Credit(
        user=created_user,
    )

    # ? Create Wallet
    wallet_number = randint(100000, 999999)
    wallet = Wallet(
        user=created_user,
        number=wallet_number,
    )
    credit.user = created_user

    db.add(created_user)
    db.add(credit)
    db.add(wallet)
    await db.commit()
    await db.refresh(created_user)

    # * Send Register SMS
    send_welcome_sms(
        phone_number=phone_number,
        full_name="{} {}".format(created_user.first_name, created_user.last_name),
    )

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
