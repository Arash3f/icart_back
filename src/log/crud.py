from typing import Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.log.exception import (
    LogNotFoundException,
)
from src.log.models import Log, LogType
from src.log.schema import LogCreate
from src.user.crud import user as user_crud
from src.user.exception import UserNotFoundException


# ---------------------------------------------------------------------------
class LogCRUD(BaseCRUD[Log, LogCreate, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        log_id: UUID,
    ) -> Type[Log] | LogNotFoundException:
        """
        ! Verify Log Existence

        Parameters
        ----------
        db
            Target database connection
        log_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        LogNotFoundException
        """
        obj = await db.get(entity=self.model, ident=log_id)
        if not obj:
            raise LogNotFoundException()

        return obj

    async def auto_generate(
        self,
        *,
        db: AsyncSession,
        user_id: UUID | None = None,
        log_type: LogType,
        detail: str | None = None,
    ) -> Type[Log] | UserNotFoundException:
        """
        ! Generate new log for user

        Parameters
        ----------
        db
            Target database connection
        user_id
            Target user
        detail
            log detail
        log_type
            log type

        Returns
        -------
        obj
            new log

        Raises
        ------
        UserNotFoundException
        """
        new_obj = self.model(
            detail=detail,
            type=log_type,
        )
        if user_id:
            user = await user_crud.verify_existence(db=db, user_id=user_id)
            new_obj.user = user
        db.add(new_obj)
        await db.commit()
        await db.refresh(new_obj)
        return new_obj


# ---------------------------------------------------------------------------
log = LogCRUD(Log)
