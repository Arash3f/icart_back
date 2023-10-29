from typing import Type
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.position_request.exception import PositionRequestNotFoundException
from src.position_request.models import PositionRequest
from src.position_request.schema import PositionRequestCreate


# ---------------------------------------------------------------------------
class PositionRequestCRUD(BaseCRUD[PositionRequest, PositionRequestCreate, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        position_request_id: UUID,
    ) -> Type[PositionRequest]:
        """
        ! Verify PositionRequest Existence

        Parameters
        ----------
        db
            Target database connection
        position_request_id
            Target Item ID

        Returns
        -------
        PositionRequestNotFoundException
        """
        obj = await db.get(entity=self.model, ident=position_request_id)
        if not obj:
            raise PositionRequestNotFoundException()

        return obj

    async def verify_not_finished_position_request_existence(
        self,
        *,
        db: AsyncSession,
        position_request_id: UUID,
    ) -> PositionRequest:
        """
        ! Verify PositionRequest Not Existence

        Parameters
        ----------
        db
            Target database connection
        position_request_id
            position_request_id: Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        PositionRequestNotFoundException
        """
        response = await db.execute(
            select(self.model).filter(
                and_(
                    self.model.id == position_request_id,
                    self.model.is_approve == False,
                ),
            ),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise PositionRequestNotFoundException()

        return obj

    async def find_by_user_id(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> PositionRequest:
        """
        ! Find Position Request by user id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target Agent user ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        PositionRequestNotFoundException
        """
        response = await db.execute(
            select(self.model).where(PositionRequest.requester_user_id == user_id),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise PositionRequestNotFoundException()

        return obj

    async def find_all_by_user_id(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> list[PositionRequest]:
        """
        ! Find All Position Request by user id

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target Agent user ID

        Returns
        -------
        objs
            Found Items

        Raises
        ------
        PositionRequestNotFoundException
        """
        response = await db.execute(
            select(self.model).where(PositionRequest.requester_user_id == user_id),
        )

        objs = response.scalars()
        return objs


# ---------------------------------------------------------------------------
position_request = PositionRequestCRUD(PositionRequest)
