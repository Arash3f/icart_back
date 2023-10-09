from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import and_, select, desc

from src import deps
from src.permission import permission_codes as permission
from src.schema import DeleteResponse, IDRequest, VerifyUserDep
from src.user.crud import user as user_crud
from src.user.models import User
from src.user_message.crud import user_message as user_message_crud
from src.user_message.models import UserMessage
from src.user_message.schema import (
    UserMessageCreate,
    UserMessageFilter,
    UserMessageRead,
    UserMessageShortRead,
    UserMessageFilterOrderFild,
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
    await user_crud.verify_existence(db=db, user_id=create_data.user_id)
    # * create user message
    obj = await user_message_crud.create(db=db, obj_in=create_data)
    return obj


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=UserMessageRead)
async def get_user_message(
    *,
    db=Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_TICKET]),
    ),
    obj_data: IDRequest,
) -> UserMessageRead:
    """
    ! Get one User Message

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
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
    message = await user_message_crud.verify_existence(
        db=db,
        user_message_id=obj_data.id,
    )
    # * Have permissions
    if not verify_data.is_valid:
        message.status = True
        db.add(message)
        await db.commit()
        await db.refresh(message)

    return message


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[UserMessageShortRead])
async def read_user_message_list(
    *,
    db=Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_USER_MESSAGE]),
    ),
    filter_data: UserMessageFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[UserMessageShortRead]:
    """
    ! Get All User Message

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
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
    query = select(UserMessage)
    # * Not Have permissions
    if not verify_data.is_valid:
        query = query.where(UserMessage.user_id == verify_data.user.id)

    # * Prepare filter fields
    filter_data.status = (
        UserMessage.status == filter_data.status
        if filter_data.status is not None
        else True
    )
    filter_data.title = (
        UserMessage.title.contains(filter_data.title)
        if filter_data.title is not None
        else True
    )
    query = query.filter(
        and_(
            filter_data.status,
            filter_data.title,
        ),
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == UserMessageFilterOrderFild.type:
                query = query.order_by(UserMessage.type.desc())
            elif field == UserMessageFilterOrderFild.number:
                query = query.order_by(UserMessage.number.desc())
        for field in filter_data.order_by.asc:
            query = query.order_by(desc(UserMessage.created_at))
            # * Add filter fields
            if field == UserMessageFilterOrderFild.type:
                query = query.order_by(UserMessage.type.asc())
            elif field == UserMessageFilterOrderFild.number:
                query = query.order_by(UserMessage.number.asc())

    # * Find All user message with filters
    message_list = await user_message_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return message_list
