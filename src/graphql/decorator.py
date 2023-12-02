from functools import wraps

from src.graphql.utils import get_token, get_user_data_from_token
from src.schema import VerifyUserDep
from src.user.crud import user as user_crud
from src.role.crud import role as role_crud

from src.auth.exception import (
    InactiveUserException,
    InvalidUserException,
    AccessDeniedException,
)


def is_login_active(func):
    """
    ! Verify User with token and check that user is active
    ? verify data saved in info object

    Raises
    ------
    UserNotAuthenticatedException
    InactiveUserException
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # ? Prepare db object and get token from kwargs
        db, token = await get_token(kwargs=kwargs)

        # ? Get Token data
        token_data = get_user_data_from_token(token=token)

        # ? Verify User
        user = await user_crud.find_by_username(
            db=db,
            username=token_data.username,
        )

        # ? Verify user activity
        if not user.is_active:
            raise InactiveUserException()

        kwargs["info"].user = user

        return func(*args, **kwargs)

    return wrapper


def is_login_active_valid(func):
    """
    ! Verify User with token and check that user is active and is valid
    ? verify data saved in info object

    Raises
    ------
    UserNotAuthenticatedException
    InvalidUserException
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # ? Prepare db object and get token from kwargs
        db, token = await get_token(kwargs=kwargs)

        # ? Get Token data
        token_data = get_user_data_from_token(token=token)

        # ? Verify User
        user = await user_crud.find_by_username(
            db=db,
            username=token_data.username,
        )

        # ? Verify user activity
        if not user.is_active or not user.is_valid:
            raise InvalidUserException()

        kwargs["info"].user = user

        return func(*args, **kwargs)

    return wrapper


def is_login_with_permissions(
    func,
    required_permissions: list[int],
):
    """
    ! Verify User with token and check that user is active and is valid and check permissions
    ? verify data saved in info object

    Raises
    ------
    UserNotAuthenticatedException
    InvalidUserException
    AccessDeniedException
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # ? Prepare db object and get token from kwargs
        db, token = await get_token(kwargs=kwargs)

        # ? Get Token data
        token_data = get_user_data_from_token(token=token)

        # ? Verify User
        user = await user_crud.verify_existence_by_username(
            db=db,
            username=token_data.username,
        )

        # ? Verify user activity
        if not user.is_active or not user.is_valid:
            raise InvalidUserException()

        # ? Verify Permissions
        role = await role_crud.verify_existence(db=db, role_id=user.role.id)

        user_permission_set = {permission.code for permission in role.permissions}
        is_valid = False
        required_permission_set = set(required_permissions)
        if required_permission_set.issubset(user_permission_set):
            is_valid = True

        if not is_valid:
            raise AccessDeniedException()

        kwargs["info"].user = user

        return func(*args, **kwargs)

    return wrapper


def is_login_have_permissions(
    func,
    required_permissions: list[int],
):
    """
    ! Verify User with token and check that user is active and is valid and just check permissions
    ? verify data saved in info object

    Raises
    ------
    UserNotAuthenticatedException
    InvalidUserException
    AccessDeniedException
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # ? Prepare db object and get token from kwargs
        db, token = await get_token(kwargs=kwargs)

        # ? Get Token data
        token_data = get_user_data_from_token(token=token)

        # ? Verify User
        user = await user_crud.verify_existence_by_username(
            db=db,
            username=token_data.username,
        )

        # ? Verify user activity
        if not user.is_active or not user.is_valid:
            raise InactiveUserException()

        verify_user: VerifyUserDep()
        verify_user.user = user

        # ? Verify Permissions
        role = await role_crud.verify_existence(db=db, role_id=user.role.id)

        user_permission_set = {permission.code for permission in role.permissions}
        required_permission_set = set(required_permissions)
        verify_user.is_valid = True

        if not required_permission_set.issubset(user_permission_set):
            verify_user.is_valid = False

        kwargs["info"].user = verify_user

        return func(*args, **kwargs)

    return wrapper
