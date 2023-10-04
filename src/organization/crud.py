from typing import Type
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.organization.exception import OrganizationNotFoundException
from src.organization.models import Organization
from src.user.models import User


# ---------------------------------------------------------------------------
class OrganizationCRUD(BaseCRUD[Organization, None, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        organization_id: UUID,
    ) -> Type[Organization]:
        """
        ! Verify Organization Existence

        Parameters
        ----------
        db
            Target database connection
        organization_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        OrganizationNotFoundException
        """
        obj = await db.get(entity=self.model, ident=organization_id)
        if not obj:
            raise OrganizationNotFoundException()

        return obj

    async def find_by_user_id(self, *, db: AsyncSession, user_id: UUID) -> Organization:
        """
        ! Find Organization by user id

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
        OrganizationNotFoundException
        """
        response = await db.execute(
            select(self.model).where(Organization.user_organization_id == user_id),
        )

        obj = response.scalar_one_or_none()
        if not obj:
            raise OrganizationNotFoundException()

        return obj

    async def get_organization_users_count(
        self,
        *,
        db: AsyncSession,
        user_id: UUID,
    ) -> bool:
        organization = await self.find_by_user_id(db=db, user_id=user_id)
        organization_users = await db.execute(
            select(func.count())
            .select_from(User)
            .where(
                User.organization == organization,
            ),
        )
        organization_users_count = organization_users.scalar()

        return organization_users_count


# ---------------------------------------------------------------------------
organization = OrganizationCRUD(Organization)
