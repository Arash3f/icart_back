from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import case, desc, func, not_, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.auth.exception import AccessDeniedException
from src.permission import permission_codes as permission
from src.schema import VerifyUserDep
from src.ticket.crud import ticket as ticket_crud
from src.ticket.models import Ticket
from src.ticket.schema import (
    TicketComplexRead,
    TicketCreate,
    TicketCreateData,
    TicketRead,
    TicketReadV2,
    TicketUpdate,
    TicketFilter,
    TicketFilterOrderFild,
)
from src.ticket_message.crud import ticket_message as ticket_message_crud
from src.ticket_message.crud import update_ticket_message_status
from src.ticket_message.models import TicketMessage, TicketMessagePosition
from src.ticket_message.schema import TicketMessageInDB
from src.user.models import User

# -------------------------------------dep--------------------------------------
router = APIRouter(prefix="/ticket", tags=["ticket"])


# ---------------------------------------------------------------------------
@router.post("/list", response_model=List[TicketReadV2])
async def read_tickets(
    *,
    db: AsyncSession = Depends(deps.get_db),
    filter_data: TicketFilter,
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_USER_MESSAGE]),
    ),
    skip: int = 0,
    limit: int = 5,
) -> List[TicketReadV2]:
    """
    ! Get All tickets

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
    my_tickets
        All my ticket list
    """
    # todo: Clean this code
    query = (
        select(
            Ticket,
            func.count(case((not_(TicketMessage.user_status), 1))),
            func.count(case((not_(TicketMessage.supporter_status), 1))),
        )
        .join(TicketMessage)
        .group_by(Ticket.id)
        .select_from(Ticket)
        .order_by(desc(Ticket.created_at), desc(Ticket.updated_at))
    )
    # * Not Have permissions
    if not verify_data.is_valid:
        query = query.where(Ticket.creator_id == verify_data.user.id)

    # * Prepare filter fields
    filter_data.type = (Ticket.type == filter_data.type) if filter_data.type else True
    filter_data.position = (
        (Ticket.position == filter_data.position) if filter_data.position else True
    )
    filter_data.important = (
        (Ticket.important == filter_data.important) if filter_data.important else True
    )
    filter_data.number = (
        (Ticket.number == filter_data.number) if filter_data.number else True
    )

    query = (
        query.filter(
            and_(
                filter_data.type,
                filter_data.position,
                filter_data.important,
                filter_data.number,
            ),
        )
        .offset(skip)
        .limit(limit)
    )

    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == TicketFilterOrderFild.type:
                query = query.order_by(Ticket.type.desc())
            elif field == TicketFilterOrderFild.position:
                query = query.order_by(Ticket.position.desc())
            elif field == TicketFilterOrderFild.important:
                query = query.order_by(Ticket.important.desc())
            elif field == TicketFilterOrderFild.number:
                query = query.order_by(Ticket.number.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == TicketFilterOrderFild.type:
                query = query.order_by(Ticket.type.asc())
            elif field == TicketFilterOrderFild.position:
                query = query.order_by(Ticket.important.asc())
            elif field == TicketFilterOrderFild.important:
                query = query.order_by(Ticket.parent_id.asc())
            elif field == TicketFilterOrderFild.number:
                query = query.order_by(Ticket.number.asc())

    res: List[TicketReadV2] = []
    response = await db.execute(query)
    obj_list = response.all()
    for i in obj_list:
        buf = i._mapping
        obj = TicketReadV2(
            title=buf["Ticket"].title,
            type=buf["Ticket"].type,
            id=buf["Ticket"].id,
            unread_user=buf["count"],
            unread_supporter=buf["count_1"],
            updated_at=buf["Ticket"].updated_at,
            created_at=buf["Ticket"].created_at,
        )
        res.append(obj)

    return res


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

    ticket.updated_at = ticket.created_at
    db.add(ticket)

    create_message = TicketMessageInDB(
        type=TicketMessagePosition.USER,
        user_status=True,
        supporter_status=False,
        text=create_data.text,
        ticket_id=ticket.id,
        creator_id=current_user.id,
    )
    await ticket_message_crud.create(db=db, obj_in=create_message)

    await db.commit()
    await db.refresh(ticket)
    return ticket


# ---------------------------------------------------------------------------
@router.get("/find", response_model=TicketComplexRead)
async def find_ticket(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_TICKET]),
    ),
    ticket_id: UUID,
) -> TicketComplexRead:
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

        # ! Update Message Status
        await update_ticket_message_status(
            db=db,
            user_read=False,
            ticket=ticket,
        )

        return ticket
    # * Verify ticket creator
    else:
        # ? Verify ticket existence
        ticket = await ticket_crud.verify_existence(db=db, ticket_id=ticket_id)

        is_creator = ticket.creator_id == verify_data.user.id
        if is_creator:
            # ! Update Message Status
            await update_ticket_message_status(
                db=db,
                user_read=True,
                ticket=ticket,
            )
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
