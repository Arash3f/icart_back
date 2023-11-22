from uuid import UUID
from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.withdraw.models import Withdraw
from src.withdraw.schemas import WithdrawCreate, WithdrawUpdate
from src.database.base_crud import BaseCRUD


# ---------------------------------------------------------------------------
class WithdrawCRUD(BaseCRUD[Withdraw, WithdrawCreate, WithdrawUpdate]):
    async def read_user_withdraw_list(self,
                                      *,
                                      db: AsyncSession,
                                      bank_card_ids: list[UUID]):
        result = await db.execute(
            select(self.model).where(self.model.bank_card.in_(bank_card_ids)).order_by(self.model.created_at.desc()))
        return result.scalars().all()


# ---------------------------------------------------------------------------
withdraw = WithdrawCRUD(Withdraw)
