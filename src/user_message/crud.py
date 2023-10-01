from typing import Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.user_message.exception import UserMessageNotFoundException
from src.user_message.models import UserMessage
from src.user_message.schema import UserMessageCreate, UserMessageUpdate


# ---------------------------------------------------------------------------
class UserMessageCRUD(BaseCRUD[UserMessage, UserMessageCreate, UserMessageUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        user_message_id: UUID,
    ) -> Type[UserMessage]:
        """
        ! Verify UserMessage Existence

        Parameters
        ----------
        db
            Target database connection
        user_message_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        UserMessageNotFoundException
        """
        obj = await db.get(entity=self.model, ident=user_message_id)
        if not obj:
            raise UserMessageNotFoundException()

        return obj


# ---------------------------------------------------------------------------
user_message = UserMessageCRUD(UserMessage)
