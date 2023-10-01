from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.auth.exception import AccessDeniedException
from src.permission import permission_codes as permission
from src.schema import VerifyUserDep
from src.ticket.crud import ticket as ticket_crud
from src.ticket.models import Ticket
from src.ticket.schema import (
    TicketCreate,
    TicketCreateData,
    TicketRead,
    TicketUpdate,
)
from src.ticket_message.crud import ticket_message as ticket_message_crud
from src.ticket_message.schema import TicketMessageInDB
from src.user.models import User

# -------------------------------------dep--------------------------------------
router = APIRouter(prefix="/ticket", tags=["ticket"])


# ---------------------------------------------------------------------------
@router.get("/my", response_model=List[TicketRead])
async def read_my_tickets(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    skip: int = 0,
    limit: int = 5,
) -> List[TicketRead]:
    """
    ! Get All my tickets

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

    Returns
    -------
    my_tickets
        All my ticket list
    """
    query = select(Ticket).where(Ticket.creator_id == current_user.id)
    my_tickets = await ticket_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return my_tickets


# ---------------------------------------------------------------------------
@router.get("/list", response_model=List[TicketRead])
async def read_tickets(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_TICKET]),
    ),
    skip: int = 0,
    limit: int = 5,
) -> List[TicketRead]:
    """
    ! Get All tickets

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

    Returns
    -------
    my_tickets
        All ticket list
    """
    my_tickets = await ticket_crud.get_multi(db=db, skip=skip, limit=limit)
    return my_tickets


# ---------------------------------------------------------------------------
@router.post("/create", response_model=TicketRead)
async def create_ticket(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    create_data: TicketCreateData,
) -> TicketRead:
    """
    ! Create New Ticket

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    create_data
        Necessary data for create ticket

    Returns
    -------
    ticket
        New Ticket
    """
    # * Generate number
    number = await ticket_crud.generate_dynamic_number(db=db)

    create_ticket = TicketCreate(
        **create_data.ticket.model_dump(),
        number=number,
        creator_id=current_user.id,
    )
    ticket = await ticket_crud.create(db=db, obj_in=create_ticket)

    create_message = TicketMessageInDB(
        text=create_data.text,
        ticket_id=ticket.id,
        creator_id=current_user.id,
    )
    await ticket_message_crud.create(db=db, obj_in=create_message)
    return ticket


# ---------------------------------------------------------------------------
@router.get("/find", response_model=TicketRead)
async def read_my_ticket_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_TICKET]),
    ),
    ticket_id: UUID,
) -> TicketRead:
    """
    ! Find Ticket

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    ticket_id
        target ticket's id

    Returns
    -------
    ticket
        Found Item

    Raises
    ------
    TicketNotFoundException
    AccessDeniedException
    """
    # * Have permissions
    if verify_data.is_valid:
        # ? Verify ticket existence
        ticket = await ticket_crud.verify_existence(db=db, ticket_id=ticket_id)

        return ticket
    # * Verify ticket creator
    else:
        # ? Verify ticket existence
        ticket = await ticket_crud.verify_existence(db=db, ticket_id=ticket_id)

        is_creator = ticket.creator_id == verify_data.user.id
        if is_creator:
            return ticket
        else:
            raise AccessDeniedException()


# ---------------------------------------------------------------------------
@router.put("/update", response_model=TicketRead)
async def update_ticket_status(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    update_data: TicketUpdate,
) -> TicketRead:
    """
    ! Update Ticket position

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        ticket new status

    Returns
    -------
    updated_ticket
        Updated ticket

    Raises
    ------
    TicketNotFoundException
    AccessDeniedException
    """
    # * Verify Ticket existence
    ticket = await ticket_crud.verify_creator(
        db=db,
        user_id=current_user.id,
        ticket_id=update_data.where.id,
    )
    # * Update Ticket Position
    updated_ticket = await ticket_crud.update(
        db=db,
        obj_current=ticket,
        obj_new=update_data.data,
    )
    return updated_ticket
