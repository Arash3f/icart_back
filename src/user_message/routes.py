from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select

from src import deps
from src.auth.exception import AccessDeniedException
from src.permission import permission_codes as permission
from src.schema import DeleteResponse, IDRequest
from src.user.crud import user as user_crud
from src.user.models import User
from src.user_message.crud import user_message as user_message_crud
from src.user_message.models import UserMessage
from src.user_message.schema import (
    UserMessageCreate,
    UserMessageFilter,
    UserMessageRead,
    UserMessageUpdate,
)

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/user_message", tags=["user_message"])


# ---------------------------------------------------------------------------
@router.delete(path="/delete", response_model=DeleteResponse)
async def delete_user_message(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.DELETE_USER_MESSAGE]),
    ),
    delete_data: IDRequest,
) -> DeleteResponse:
    """
    ! Delete User Message

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    delete_data
        Necessary data for delete user_message

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    UserMessageNotFoundException
    """
    # * Verify user_message existence
    await user_message_crud.verify_existence(db=db, user_message_id=delete_data.id)
    # * Delete user message
    await user_message_crud.delete(db=db, id=delete_data.id)
    return DeleteResponse(result="User Message Deleted Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/create", response_model=UserMessageRead)
async def create_user_message(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CREATE_USER_MESSAGE]),
    ),
    create_data: UserMessageCreate,
) -> UserMessageRead:
    """
    ! Create New User Message

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    create_data
        Necessary data for create user_message

    Returns
    -------
    obj
        New user_message

    Raises
    ------
    UserNotFoundException
    """
    # * Verify user existence
    await user_crud.verify_user_existence(db=db, user_id=create_data.user_id)
    # * create user message
    obj = await user_message_crud.create(db=db, obj_in=create_data)
    return obj


# ---------------------------------------------------------------------------
@router.put(path="/update_status", response_model=UserMessageRead)
async def update_user_message(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    update_data: UserMessageUpdate,
) -> UserMessageRead:
    """
    ! Update User Message's Status

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update user_message's status

    Returns
    -------
    obj
        Updated user_message

    Raises
    ------
    UserMessageNotFoundException
    AccessDeniedException
    """
    # * Verify user_message existence
    obj = await user_message_crud.verify_existence(
        db=db,
        user_message_id=update_data.where.id,
    )
    if obj.user_id == current_user.id:
        obj.status = True
        await db.commit()
        await db.refresh(obj)
    else:
        raise AccessDeniedException()
    return obj


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=UserMessageRead)
async def get_user_message(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_USER_MESSAGE]),
    ),
    obj_data: IDRequest,
) -> UserMessageRead:
    """
    ! Get one User Message

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target UserMessage's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    UserMessageNotFoundException
    """
    # * Verify user_message existence
    obj = await user_message_crud.verify_existence(db=db, user_message_id=obj_data.id)
    return obj


# ---------------------------------------------------------------------------
@router.get(path="/list", response_model=List[UserMessageRead])
async def get_user_message_list(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_USER_MESSAGE]),
    ),
    filter_data: UserMessageFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[UserMessageRead]:
    """
    ! Get All User Message

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
    message_list
        List of user message
    """
    # * Prepare filter fields
    filter_data.status = (
        UserMessage.stasus == filter_data.status if filter_data.status else False
    )
    # * Add filter fields
    query = select(UserMessage).filter(or_(filter_data.return_all, filter_data.stasus))
    # * Find All user message with filters
    message_list = await user_message_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return message_list


# ---------------------------------------------------------------------------
@router.get(path="/my", response_model=List[UserMessageRead])
async def get_user_message_list_my(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    filter_data: UserMessageFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[UserMessageRead]:
    """
    ! Get All User Message

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
        List of user message
    """
    # * Prepare filter fields

    filter_data.status = (
        UserMessage.stasus == filter_data.status if filter_data.stasus else False
    )

    query = select(UserMessage).where(UserMessage.user_id == current_user.id)
    # * Add filter fields
    query = query.filter(or_(filter_data.return_all, filter_data.stasus))
    # * Find All user message with filters
    obj_list = await user_message_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list
