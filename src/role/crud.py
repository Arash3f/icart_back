import uuid
from typing import Type
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.role.exception import (
    RoleHaveUserException,
    RoleNameIsDuplicatedException,
    RoleNotFoundException,
)
from src.role.models import Role, RolePermission
from src.role.schema import RoleCreate, RolePermissionCreate, RoleUpdate


# ---------------------------------------------------------------------------
class RoleCRUD(BaseCRUD[Role, RoleCreate, RoleUpdate]):
    async def find_by_name(self, db: AsyncSession, name: str) -> Role | None:
        """
        ! Find role by name

        Parameters
        ----------
        db
            Target database connection
        name
            Target role's name

        Returns
        -------
        obj
            Found role

        """
        response = await db.execute(select(self.model).where(self.model.name == name))
        obj = response.scalar_one_or_none()
        return obj

    async def verify_existence_by_name(
        self,
        *,
        db: AsyncSession,
        name: str,
    ) -> Type[Role] | RoleNotFoundException:
        """
         ! Verify Role Existence by name

        Parameters
        ----------
        db
            Target database connection
        name
            Target role's name

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        RoleNotFoundException
        """
        res = await db.execute(select(self.model).where(self.model.name == name))
        obj = res.scalar_one_or_none()
        if not obj:
            raise RoleNotFoundException()

        return obj

    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        role_id: UUID,
    ) -> Role | RoleNotFoundException:
        """
        ! Verify Role Existence

        Parameters
        ----------
        db
            Target database connection
        role_id
            Target role's ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        RoleNotFoundException
        """
        response = await db.execute(select(self.model).where(self.model.id == role_id))

        obj = response.scalar_one_or_none()
        if not obj:
            raise RoleNotFoundException()

        return obj

    async def verify_duplicate_name(
        self,
        *,
        db: AsyncSession,
        name: str,
        exception_name: str = None,
    ) -> Role | RoleNameIsDuplicatedException:
        """
        ! Verify role duplicate name

        Parameters
        ----------
        db
            Target database connection
        name
            Target Item name
        exception_name
            Exception role name

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        RoleNameIsDuplicatedException
        """
        response = await db.execute(
            select(self.model).where(
                and_(self.model.name == name, self.model.name != exception_name),
            ),
        )

        obj = response.scalar_one_or_none()
        if obj:
            raise RoleNameIsDuplicatedException()

        return obj

    async def verify_connections(
        self,
        *,
        db: AsyncSession,
        role_id: UUID,
    ) -> bool | RoleHaveUserException:
        """
        ! Verify Role do not have any connections

        Parameters
        ----------
        db
            Target database connection
        role_id
            Target Role's id

        Returns
        -------
        response
            Result of operation

        Raises
        ------
        RoleHaveUserException

        """
        target_role = await self.verify_existence(db=db, role_id=role_id)
        if len(target_role.users):
            raise RoleHaveUserException()

        return True


# ---------------------------------------------------------------------------
class RolePermissionCRUD(BaseCRUD[RolePermission, RolePermissionCreate, None]):
    async def verify_permission_by_role_id(
        self,
        db: AsyncSession,
        role_id: uuid.UUID,
        permission_id: uuid.UUID,
    ) -> RolePermission | None:
        """
        ! Verify permission by role id

        Parameters
        ----------
        db
            Target database connection
        role_id
            Target role's id
        permission_id
            Target permission's id

        Returns
        -------
        obj
            Found Item or None
        """
        response = await db.execute(
            select(self.model).where(
                and_(
                    self.model.role_id == role_id,
                    self.model.permission_id == permission_id,
                ),
            ),
        )
        obj = response.scalar_one_or_none()
        return obj


# ---------------------------------------------------------------------------
role = RoleCRUD(Role)
role_permission = RolePermissionCRUD(RolePermission)
