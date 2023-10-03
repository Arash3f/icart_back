from sqlalchemy import and_, update
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
    query = update(TicketMessage).where(
        and_(
            TicketMessage.ticket_id == ticket.id,
            TicketMessage.creator_id == ticket.creator_id,
        ),
    )
    if user_read:
        query = query.values(
            {"user_status": True},
        )
    else:
        query = query.values(
            {"supporter_status": True},
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
