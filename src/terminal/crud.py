from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.terminal.exception import TerminalNotFoundException
from src.terminal.models import Terminal


# ---------------------------------------------------------------------------
class TerminalCRUD(BaseCRUD[Terminal, None, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        terminal_id: UUID,
    ) -> Type[Terminal]:
        """
        ! Verify Fee Existence

        Parameters
        ----------
        db
            Target database connection
        terminal_id
            Target terminal's ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        TerminalNotFoundException
        """
        obj = await db.get(entity=self.model, ident=terminal_id)
        if not obj:
            raise TerminalNotFoundException()

        return obj

    async def verify_existence_by_number(
        self,
        *,
        db: AsyncSession,
        terminal_number: str,
    ) -> Type[Terminal]:
        """
        ! Verify terminal Existence

        Parameters
        ----------
        db
            Target database connection
        terminal_number
            Target terminal's number

        Returns
        -------
        response
            Found Item

        Raises
        ------
        TerminalNotFoundException
        """
        response = await db.execute(
            select(self.model).where(Terminal.number == terminal_number),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise TerminalNotFoundException()

        return obj


# ---------------------------------------------------------------------------
terminal = TerminalCRUD(Terminal)
