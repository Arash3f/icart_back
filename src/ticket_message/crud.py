from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.ticket.models import Ticket
from src.ticket_message.models import TicketMessage
from src.ticket_message.schema import TicketMessageCreate, TicketMessageUpdate


# ---------------------------------------------------------------------------
async def update_ticket_message_status(
    *,
    db: AsyncSession,
    user_read: bool,
    ticket: Ticket,
) -> bool:
    """
    ! Update ticket message status

    Parameters
    ----------
    db
        Target database connection
    user_read
        Update for user or supporter
    ticket
        target tecket

    Returns
    -------
    response
        Result of operation
    """
    query = update(TicketMessage).where(TicketMessage.ticket_id == ticket.id)
    values = {
        "user_status": TicketMessage.user_status,
        "supporter_status": TicketMessage.supporter_status,
    }
    if user_read:
        where = TicketMessage.creator_id == ticket.creator_id
        values["user_status"] = True
    else:
        # todo: This code not work correctly for admin ?!?
        where = TicketMessage.creator_id != ticket.creator_id
        values["supporter_status"] = True

    query = query.where(
        where,
    ).values(
        values,
    )

    await db.execute(query)
    await db.commit()
    return True


class TicketMessageCRUD(
    BaseCRUD[TicketMessage, TicketMessageCreate, TicketMessageUpdate],
):
    pass


# ---------------------------------------------------------------------------
ticket_message = TicketMessageCRUD(TicketMessage)
