from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.auth.exception import AccessDeniedException
from src.permission import permission_codes as permission
from src.schema import VerifyUserDep
from src.ticket.crud import ticket as ticket_crud
from src.ticket_message.crud import ticket_message as ticket_message_crud
from src.ticket_message.models import TicketMessagePosition
from src.ticket_message.schema import (
    TicketMessageCreate,
    TicketMessageInDB,
    TicketMessageRead,
)

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/ticket_message", tags=["ticket_message"])


# ---------------------------------------------------------------------------
@router.post("/create", response_model=TicketMessageRead)
async def create_message(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.RESPONSE_TICKET]),
    ),
    create_message_in: TicketMessageCreate,
) -> TicketMessageRead:
    """
    ! Create new message for ticket

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    create_message_in
        Necessary data for create message

    Returns
    -------
    new_message
        New message

    Raises
    ------
    TicketNotFoundException
    TicketClosePositionException
    AccessDeniedException
    """
    # ? Verify Ticket existence
    ticket = await ticket_crud.verify_existence(
        db=db,
        ticket_id=create_message_in.ticket_id,
    )
    # ? Verify Ticket Position is not Close
    await ticket_crud.verify_position_is_not_close(db=db, ticket_id=ticket.id)

    user_status = True
    supporter_status = False
    message_type = TicketMessagePosition.USER
    if ticket.creator_id != verify_data.user.id:
        if not verify_data.is_valid:
            raise AccessDeniedException()
        message_type = TicketMessagePosition.SUPPORTER
        user_status = False
        supporter_status = True

    create_data = TicketMessageInDB(
        **create_message_in.model_dump(),
        type=message_type,
        user_status=user_status,
        supporter_status=supporter_status,
        creator_id=verify_data.user.id,
    )
    new_message = await ticket_message_crud.create(db=db, obj_in=create_data)

    # ? Update ticket's updated_at ( use for ordering )
    ticket.updated_at = new_message.created_at
    db.add(ticket)
    await db.commit()

    return new_message
