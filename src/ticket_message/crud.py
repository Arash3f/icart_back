from src.database.base_crud import BaseCRUD
from src.ticket_message.models import TicketMessage
from src.ticket_message.schema import TicketMessageCreate


# ---------------------------------------------------------------------------
class TicketMessageCRUD(BaseCRUD[TicketMessage, TicketMessageCreate, None]):
    pass


# ---------------------------------------------------------------------------
ticket_message = TicketMessageCRUD(TicketMessage)
