from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contract.exception import ContractNotFoundException
from src.contract.models import Contract
from src.contract.schema import ContractCreate
from src.database.base_crud import BaseCRUD


# ---------------------------------------------------------------------------
class ContractCRUD(BaseCRUD[Contract, ContractCreate, None]):
    async def verify_existence(
        self,
        *,
        db: AsyncSession,
        contract_id: UUID,
    ) -> Type[Contract]:
        """
        ! Verify Contract Existence

        Parameters
        ----------
        db
            Target database connection
        contract_id
            Target Item ID

        Returns
        -------
        obj
            Found Item

        Raises
        ------
        ContractNotFoundException
        """
        obj = await db.get(entity=self.model, ident=contract_id)
        if not obj:
            raise ContractNotFoundException()

        return obj

    async def find_by_number(
        self,
        *,
        db: AsyncSession,
        number: str,
    ) -> Type[Contract]:
        """
        ! Find Contract by number

        Parameters
        ----------
        db
            Target database connection
        number
            Target number

        Returns
        -------
        found_item
            Found Item
        """
        response = await db.execute(
            select(self.model).where(self.model.number == number),
        )

        found_item = response.scalar_one_or_none()
        return found_item


# ---------------------------------------------------------------------------
contract = ContractCRUD(Contract)
