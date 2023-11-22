from src import deps
from src.user.models import User
from src.withdraw.models import Withdraw
from src.band_card.exception import BankCardNotFound
from src.withdraw.crud import withdraw as withdraw_crud
from src.permission import permission_codes
from src.band_card.crud import bank_card as bank_card_crud
from src.withdraw.schemas import (
    WithdrawCreate,
    WithdrawUpdate,
    WithdrawRead,
    WithdrawReadWithBankInfo
)
from src.withdraw.exception import WithdrawNotFound

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/withdraw", tags=["withdraw"])


# ---------------------------------------------------------------------------
@router.get("/me/list", response_model=list[WithdrawReadWithBankInfo])
async def get_my_withdraw_list(*,
                               db: AsyncSession = Depends(deps.get_db),
                               current_user: User = Depends(deps.get_current_user())):
    bank_card_list = await bank_card_crud.read_user_bank_card_list(db=db, user_id=current_user.id)
    bank_card_ids = [bank_card.id for bank_card in bank_card_list]
    withdraw_list = await withdraw_crud.read_user_withdraw_list(db=db, bank_card_ids=bank_card_ids)
    return withdraw_list


# ---------------------------------------------------------------------------
@router.get("/me/{withdraw_id}", response_model=WithdrawReadWithBankInfo)
async def get_my_withdraw_info(*,
                               db: AsyncSession = Depends(deps.get_db),
                               current_user: User = Depends(deps.get_current_user()),
                               withdraw_id: UUID):
    bank_card_list = await bank_card_crud.read_user_bank_card_list(db=db, user_id=current_user.id)
    withdraw = await withdraw_crud.get(db=db, item_id=withdraw_id)
    if not withdraw:
        raise WithdrawNotFound()
    if withdraw.bank_card_id not in [bank_card.id for bank_card in bank_card_list]:
        raise WithdrawNotFound()
    return withdraw


# ---------------------------------------------------------------------------
@router.post("/create", response_model=WithdrawReadWithBankInfo)
async def create_withdraw_request(*,
                                  db: AsyncSession = Depends(deps.get_db),
                                  current_user: User = Depends(deps.get_current_user()),
                                  withdraw_in: WithdrawCreate):
    bank_card = await bank_card_crud.get(db=db, item_id=withdraw_in.bank_card_id)
    cash = current_user.cash
    if withdraw_in.amount > cash.balance:
        raise
    if current_user.id != bank_card.user_id:
        raise BankCardNotFound()
    created_withdraw = await withdraw_crud.create(db=db, obj_in=withdraw_in)
    return created_withdraw

    # ---------------------------------------------------------------------------


@router.delete("/delete/{withdraw_id}", response_model=WithdrawReadWithBankInfo)
async def delete_withdraw_request(*,
                                  db: AsyncSession = Depends(deps.get_db),
                                  current_user: User = Depends(deps.get_current_user()),
                                  withdraw_id: UUID):
    bank_card_list = await bank_card_crud.read_user_bank_card_list(db=db, user_id=current_user.id)
    withdraw = await withdraw_crud.get(db=db, item_id=withdraw_id)
    if not withdraw:
        raise WithdrawNotFound()
    if withdraw.bank_card_id not in [bank_card.id for bank_card in bank_card_list]:
        raise WithdrawNotFound()
    deleted_withdraw = withdraw_crud.delete(db=db, item_id=withdraw_id)
    return deleted_withdraw


# ---------------------------------------------------------------------------
@router.put("/validate/{withdraw_id}", response_model=WithdrawReadWithBankInfo)
async def accept_or_deny_withdraw(*,
                                  db: AsyncSession = Depends(deps.get_db),
                                  current_user: User = Depends(deps.get_current_user_with_permissions()),
                                  withdraw_id: UUID,
                                  verify: bool):
    withdraw = await withdraw_crud.get(db=db, item_id=withdraw_id)
    if not withdraw:
        raise WithdrawNotFound()
    update_schema = {"is_verified": verify}
    updated_withdraw = await withdraw_crud.update(db=db, obj_current=withdraw, obj_new=update_schema)
    return updated_withdraw
