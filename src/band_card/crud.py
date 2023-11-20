from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.base_crud import BaseCRUD
from src.band_card.models import BankCard
from src.band_card.schemas import BankCardCreate, BankCardUpdate


# ----------------------------------------------------------------
class BankCardCRUD(BaseCRUD[BankCard, BankCardCreate, BankCardUpdate]):
    async def read_user_bank_card_list(self,
                                       *,
                                       db: AsyncSession,
                                       user_id: UUID):
        result = await db.execute(select(self.model).where(
            self.model.user_id == user_id))
        return result.scalars().all()

    async def read_user_bank_card(self,
                                  *,
                                  db: AsyncSession,
                                  user_id: UUID,
                                  card_id):
        result = await db.execute(select(self.model).where(and_(self.model.id == card_id, self.model.user_id == user_id)))
        return result.scalar_one_or_none()

    async def reab_by_bank_card_number(self,
                                       *,
                                       db: AsyncSession,
                                       card_number: str):
        result = await db.execute(select(self.model).where(self.model.card_number == card_number))
        return result.scalar_one_or_none()


# ----------------------------------------------------------------
bank_card = BankCardCRUD(BankCard)
