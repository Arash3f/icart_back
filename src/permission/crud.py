from typing import List, Sequence, Type
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.permission.exception import PermissionNotFoundException
from src.permission.models import Permission


# ---------------------------------------------------------------------------
class PermissionCRUD(BaseCRUD[Permission, None, None]):
    async def find_by_code(self, db: AsyncSession, code: int) -> Permission | None:
        """
        ! Find Permission with code

        Parameters
        ----------
        db
            Target database connection
        code
            Target permissions code

        Returns
        -------
        obj
            Found permission
        """
        response = await db.execute(select(self.model).where(self.model.code == code))
        return response.scalar_one_or_none()

    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        permission_id: UUID,
    ) -> Type[Permission] | PermissionNotFoundException:
        """
        ! Verify Permission Existence

        Parameters
        ----------
        db
            Target database connection
        permission_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        PermissionNotFoundException
        """
        obj = await db.get(entity=self.model, ident=permission_id)
        if not obj:
            raise PermissionNotFoundException()

        return obj

    async def verify_permission_list_existence(
        self,
        *,
        db: AsyncSession,
        list_ids: List[UUID],
    ) -> Sequence[Permission] | PermissionNotFoundException:
        """
        ! Verify Permission List Existence

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
        PermissionNotFoundException
        """
        response = await db.execute(
            select(func.count())
            .select_from(self.model)
            .where(
                self.model.id.in_(list_ids),
            ),
        )
        response = response.scalar()
        if response != len(list_ids):
            raise PermissionNotFoundException()
        return response

    # ---------------------------------------------------------------------------


permission = PermissionCRUD(Permission)
