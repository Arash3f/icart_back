from typing import Type
from uuid import UUID

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


# ---------------------------------------------------------------------------
contract = ContractCRUD(Contract)
