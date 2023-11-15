from typing import Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.cooperation_request.exception import (
    CooperationRequestNotFoundException,
)
from src.cooperation_request.models import CooperationRequest
from src.cooperation_request.schema import CooperationRequestCreate


# ---------------------------------------------------------------------------
class CooperationRequestCRUD(
    BaseCRUD[CooperationRequest, CooperationRequestCreate, None],
):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        cooperation_request_id: UUID,
    ) -> Type[CooperationRequest] | CooperationRequestNotFoundException:
        """
        ! Verify CooperationRequest Existence

        Parameters
        ----------
        db
            Target database connection
        cooperation_request_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        CooperationRequestNotFoundException
        """
        obj = await db.get(entity=self.model, ident=cooperation_request_id)
        if not obj:
            raise CooperationRequestNotFoundException()

        return obj


# ---------------------------------------------------------------------------
cooperation_request = CooperationRequestCRUD(CooperationRequest)
