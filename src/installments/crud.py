from typing import Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.installments.exception import (
    InstallmentsNotFoundException,
)
from src.installments.models import Installments
from src.installments.schema import InstallmentsCreate


# ---------------------------------------------------------------------------
class InstallmentsCRUD(BaseCRUD[Installments, InstallmentsCreate, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        installments_id: UUID,
    ) -> Type[Installments]:
        """
        ! Verify Installments Existence

        Parameters
        ----------
        db
            Target database connection
        installments_id
            Target Installments ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        InstallmentsNotFoundException
        """
        obj = await db.get(entity=self.model, ident=installments_id)
        if not obj:
            raise InstallmentsNotFoundException()

        return obj


# ---------------------------------------------------------------------------
installments = InstallmentsCRUD(Installments)
