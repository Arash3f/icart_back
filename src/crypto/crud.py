from typing import Type
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crypto.exception import (
    CryptoNameIsDuplicatedException,
    CryptoNotFoundException,
)
from src.crypto.models import Crypto
from src.crypto.schema import CryptoCreate, CryptoUpdate
from src.database.base_crud import BaseCRUD


# ---------------------------------------------------------------------------
class CryptoCRUD(BaseCRUD[Crypto, CryptoCreate, CryptoUpdate]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        crypto_id: UUID,
    ) -> Type[Crypto]:
        """
        ! Verify Crypto Existence

        Parameters
        ----------
        db
            Target database connection
        crypto_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        CryptoNotFoundException
        """
        obj = await db.get(entity=self.model, ident=crypto_id)
        if not obj:
            raise CryptoNotFoundException()

        return obj

    async def verify_duplicate_name(
        self,
        *,
        db: AsyncSession,
        name: str,
        exception_name: str = None,
    ) -> Crypto:
        """
        ! Verify crypto duplicate name

        Parameters
        db
            Target database connection
        name
            Target crypto name
        exception_name
            Exception crypto name

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        CryptoNameIsDuplicatedException
        """
        response = await db.execute(
            select(self.model).where(
                and_(Crypto.name == name, Crypto.name != exception_name),
            ),
        )

        obj = response.scalar_one_or_none()
        if obj:
            raise CryptoNameIsDuplicatedException()

        return obj


# ---------------------------------------------------------------------------
crypto = CryptoCRUD(Crypto)
