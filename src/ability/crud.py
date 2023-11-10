from typing import List, Sequence, Type
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ability.exception import (
    AbilityNameIsDuplicatedException,
    AbilityNotFoundException,
)
from src.ability.models import Ability
from src.ability.schema import AbilityCreate, AbilityUpdate
from src.database.base_crud import BaseCRUD


# ---------------------------------------------------------------------------
class AbilityCRUD(BaseCRUD[Ability, AbilityCreate, AbilityUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        ability_id: UUID,
    ) -> Type[Ability] | AbilityNotFoundException:
        """
        ! Verify Ability Existence

        Parameters
        ----------
        db
            Target database connection
        ability_id
            Target Item ID

        Returns
        -------
        found_ability
            Found Item

        Raises
        ------
        AbilityNotFoundException
            Ability with this id not exist
        """
        found_ability = await db.get(entity=self.model, ident=ability_id)
        if not found_ability:
            raise AbilityNotFoundException()

        return found_ability

    async def verify_existence_by_name(
        self,
        *,
        db: AsyncSession,
        name: str,
    ) -> Type[Ability] | AbilityNotFoundException:
        """
        ! Verify Ability Existence by name

        Parameters
        ----------
        db
            Target database connection
        name
            Target Item name

        Returns
        -------
        found_ability
            Found Item

        Raises
        ------
        AbilityNotFoundException
            Ability with this id not exist
        """
        response = await db.execute(
            select(self.model).where(
                self.model.name == name,
            ),
        )

        found_ability = response.scalar_one_or_none()
        if not found_ability:
            raise AbilityNotFoundException()

        return found_ability

    async def verify_list_existence(
        self,
        *,
        db: AsyncSession,
        list_ids: List[UUID],
    ) -> Sequence[Ability] | AbilityNotFoundException:
        """
        Verify list of abilities existence

        Parameters
        ----------
        db
            Target database connection
        list_ids
            Target Item IDs

        Returns
        -------
        response
             Found Items

        Raises
        ------
        AbilityNotFoundException
            Some of the abilities not exist
        """
        response = await db.execute(
            select(self.model).where(self.model.id.in_(list_ids)),
        )
        response = response.scalars().all()
        if len(response) != len(list_ids):
            raise AbilityNotFoundException()
        return response

    async def verify_duplicate_name(
        self,
        *,
        db: AsyncSession,
        name: str,
        exception_name: str = None,
    ) -> bool | AbilityNameIsDuplicatedException:
        """
        ! Verify Ability duplicate name with exception

        Parameters
        ----------
        db
            Target database connection
        name
            Target Ability name
        exception_name
            Exception Ability name

        Returns
        -------
        response
            result of operation

        Raises
        ------
        AbilityNameIsDuplicatedException
            Ability with this filter is exist
        """
        response = await db.execute(
            select(self.model).where(
                and_(Ability.name == name, Ability.name != exception_name),
            ),
        )

        obj = response.scalar_one_or_none()
        if obj:
            raise AbilityNameIsDuplicatedException()

        return True

    async def find_by_name(self, db: AsyncSession, name: str) -> Ability | None:
        """
        ! Find ability by name

        Parameters
        ----------
        db
            Target database connection
        name
            Target ability's name

        Returns
        -------
        obj
            Found ability
        """
        response = await db.execute(select(self.model).where(self.model.name == name))
        obj = response.scalar_one_or_none()
        return obj


# ---------------------------------------------------------------------------
ability = AbilityCRUD(Ability)
