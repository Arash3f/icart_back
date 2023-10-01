from typing import Type
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.location.exception import (
    LocationNameIsDuplicatedException,
    LocationNotFoundException,
    LocationParentNotFoundException,
)
from src.location.models import Location
from src.location.schema import LocationCreate, LocationUpdate


# ---------------------------------------------------------------------------
class LocationCRUD(BaseCRUD[Location, LocationCreate, LocationUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        location_id: UUID,
        parent_exception: bool = False,
    ) -> Type[Location]:
        """
        ! Verify Location Existence

        Parameters
        ----------
        db
            Target database connection
        location_id
            Target Item ID
        parent_exception
            Return Exception for parent ID?

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        LocationParentNotFoundException
        LocationNotFoundException
        """
        obj = await db.get(entity=self.model, ident=location_id)
        if not obj:
            if parent_exception:
                raise LocationParentNotFoundException()
            else:
                raise LocationNotFoundException()

        return obj

    async def find_by_name(self, *, db: AsyncSession, name: str) -> Location:
        """
        ! Find Location by name

        Parameters
        ----------
        db
            Target database connection
        name
            Target Parent name

        Returns
        -------
        obj
            Found Item
        """
        response = await db.execute(select(self.model).where(Location.name == name))

        obj = response.scalar_one_or_none()

        return obj

    async def verify_duplicate_name(
        self,
        *,
        db: AsyncSession,
        name: str,
        exception_name: str = None,
    ) -> Location:
        """
        ! Verify location name is duplicated

        Parameters
        ----------
        db
            Target database connection
        name
            Target Parent name
        exception_name
            Exception location name

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        LocationNameIsDuplicatedException
        """
        response = await db.execute(
            select(self.model).where(
                and_(Location.name == name, Location.name != exception_name),
            ),
        )

        obj = response.scalar_one_or_none()
        if obj:
            raise LocationNameIsDuplicatedException()

        return obj


# ---------------------------------------------------------------------------
location = LocationCRUD(Location)
