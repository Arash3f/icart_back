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
    OneTimePasswordRequestIn,
    UserRegisterIn,
    VerifyUsernameAndNationalCode,
)
from src.core.config import settings
from src.core.security import generate_access_token, hash_password
from src.credit.models import Credit
from src.role.crud import role as role_crud
from src.schema import ResultResponse
from src.user.crud import user as user_crud
from src.user.models import User
from src.verify_phone.crud import verify_phone as verify_phone_crud

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
    if not user.is_active:
        raise InactiveUserException()

    access_token_expire_time = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    role = await role_crud.get(db=db, item_id=user.role.id)

    token = generate_access_token(
        data={"username": user.username, "role": role.name},
        expire_delta=access_token_expire_time,
    )
    access_token: AccessToken = AccessToken(access_token=token, token_type="bearer")
    return access_token


@router.post("/login/one_time_password")
async def login_for_access_token(
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
    user = await auth_crud.authenticate_v2(
        db=db,
        username=login_form.username,
        password=login_form.password,
    )

    if not user:
        raise IncorrectUsernameOrPasswordException()
    if not user.is_active:
        raise InactiveUserException()

    access_token_expire_time = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    role = await role_crud.get(db=db, id=user.role_id)

    token = generate_access_token(
        data={"user_name": user.user_name, "role": role.name},
        expire_delta=access_token_expire_time,
    )
    access_token: AccessToken = AccessToken(access_token=token, token_type="bearer")
    return access_token


# ---------------------------------------------------------------------------
@router.post(
    "/one_time_password/request",
    response_model=ResultResponse,
    status_code=200,
)
async def current_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    request_data: OneTimePasswordRequestIn,
) -> ResultResponse:
    """
    ! Request one time password

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
    username = request_data.username

    # ? Generate dynamic password
    one_time_password = randint(100000, 999999)
    # ? Find user
    user = await user_crud.verify_existence_by_username(db=db, username=username)
    # ? Update user data
    user.one_time_password = one_time_password
    user.expiration_password_at = datetime.now() + timedelta(
        minutes=settings.DYNAMIC_PASSWORD_EXPIRE_MINUTES,
    )
    db.add(user)
    await db.commit()
    # ? Send SMS to user's phone
    # send_one_time_password_sms(phone_number=user.phone_number, code=one_time_password)

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
async def register_user(
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
    current_time = datetime.now(tz=timezone.utc)
    role = await role_crud.verify_existence_by_name(db=db, name="کاربر ساده")

    # todo: verify phone number and national code with web server

    # ? Verify Phone Number
    verify_code_number = await verify_phone_crud.find_by_phone_number(
        db=db,
        phone_number=phone_number,
    )
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
    created_user = User()
    created_user.username = phone_number
    created_user.password = hash_password(register_data.password)
    created_user.role_id = role.id
    created_user.first_name = register_data.first_name
    created_user.last_name = register_data.last_name
    created_user.national_code = register_data.national_code

    # ? Create Credit
    credit = Credit()
    credit.user = created_user

    # todo:  Create Credit 2
    # credit = Credit()
    # credit.user = created_user

    db.add(created_user)
    db.add(credit)
    await db.commit()
    await db.refresh(created_user)

    return ResultResponse(result="User Created Successfully")
