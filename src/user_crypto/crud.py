from typing import Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_crud import BaseCRUD
from src.user_crypto.exception import UserCryptoNotFoundException
from src.user_crypto.models import UserCrypto
from src.user_crypto.schema import UserCryptoCreate, UserCryptoUpdate


# ---------------------------------------------------------------------------
class UserCryptoCRUD(BaseCRUD[UserCrypto, UserCryptoCreate, UserCryptoUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        user_crypto_id: UUID,
    ) -> Type[UserCrypto]:
        """
        ! Verify UserCrypto Existence

        Parameters
        ----------
        db
            Target database connection
        user_crypto_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        UserCryptoNotFoundException
        """
        obj = await db.get(entity=self.model, ident=user_crypto_id)
        if not obj:
            raise UserCryptoNotFoundException()

        return obj


# ---------------------------------------------------------------------------
user_crypto = UserCryptoCRUD(UserCrypto)
