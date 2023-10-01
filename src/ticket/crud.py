from random import randint
from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exception import AccessDeniedException
from src.database.base_crud import BaseCRUD
from src.ticket import schema
from src.ticket.exception import (
    TicketClosePositionException,
    TicketNotFoundException,
)
from src.ticket.models import Ticket, TicketPosition


# ---------------------------------------------------------------------------
class TicketCRUD(BaseCRUD[Ticket, schema.TicketCreate, schema.TicketUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        ticket_id: UUID,
    ) -> Type[Ticket]:
        """
        ! Verify Ticket Existence

        Parameters
        ----------
        db
            Target database connection
        ticket_id
            Target ticket's ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        TicketNotFoundException
        """
        obj = await db.get(entity=self.model, ident=ticket_id)
        if not obj:
            raise TicketNotFoundException()

        return obj

    async def verify_creator(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
        ticket_id: UUID,
    ) -> Type[Ticket]:
        """
        ! Verify Ticket's creator

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target User id
        ticket_id
            Target ticket's ID

        Returns
        -------
        obj
            Verify ticket

        Raises
        ------
        TicketNotFoundException
        AccessDeniedException
        """
        obj = await self.verify_existence(db=db, ticket_id=ticket_id)
        # ? Verify Ticket Access
        if obj.creator_id != user_id:
            raise AccessDeniedException()

        return obj

    async def verify_position_is_not_close(
        self,
        *,
        db: AsyncSession,
        ticket_id: UUID,
    ) -> Type[Ticket]:
        """
        ! Verify Ticket position is not close

        Parameters
        ----------
        db
            Target database connection
        ticket_id
            Target Ticket id

        Returns
        -------
        obj
            found ticket

        Raises
        ------
        TicketNotFoundException
        TicketClosePositionException
        """
        obj = await self.verify_existence(db=db, ticket_id=ticket_id)
        # ? Verify Ticket Access
        if obj.position == TicketPosition.CLOSE:
            raise TicketClosePositionException()

        return obj

    async def find_by_number(self, *, db: AsyncSession, number: int) -> Type[Ticket]:
        """
        ! Find Ticket by number

        Parameters
        ----------
        db
            Target database connection
        number
            Target ticket number

        Returns
        -------
        found_item
            Found Item

        """
        response = await db.execute(
            select(self.model).where(self.model.number == number),
        )

        found_item = response.scalar_one_or_none()
        return found_item

    async def generate_dynamic_number(self, *, db: AsyncSession) -> int:
        """
        ! Generate dynamic number

        Parameters
        ----------
        db
            Target database connection

        Returns
        -------
        code
            generated number
        """
        number = 0
        while not number:
            generate_number = randint(100000, 999999)
            is_duplicate = await self.find_by_number(db=db, number=generate_number)
            if not is_duplicate:
                number = generate_number

        return number


# ---------------------------------------------------------------------------
ticket = TicketCRUD(Ticket)
