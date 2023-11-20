from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, BackgroundTasks

from src import deps
from src.user.models import User
from src.band_card.exception import BankCardNotFound, BankCardDuplicate
from src.band_card.crud import bank_card as bank_card_crud
from src.band_card.schemas import (BankCardRead,
                                   BankCardCreate,
                                   BankCardUpdate)
# -------------------------------------------------------------


async def verify_bank_card(user_id: UUID,
                           card_number: str,
                           shaba_number: str):
    pass
# -------------------------------------------------------------
router = APIRouter("/bank_card", tags=["bank_card"])


# -------------------------------------------------------------
@router.get("/list", response_model=list[BankCardRead])
async def get_user_bank_card_list(*,
                                  db: AsyncSession = Depends(deps.get_db),
                                  current_user: User = Depends(deps.get_current_user())) -> list[BankCardRead]:
    obj_list = await bank_card_crud.read_user_bank_card_list(db=db, user_id=current_user.id)
    return obj_list


# -------------------------------------------------------------
@router.get("/{bank_card_id}", response_model=BankCardRead)
async def get_user_bank_card(*,
                             db: AsyncSession = Depends(deps.get_db),
                             current_user: User = Depends(
                                 deps.get_current_user()),
                             bank_card_id: UUID):
    obj = await bank_card_crud.read_user_bank_card(db=db, user_id=current_user.id, card_id=bank_card_id)
    if not obj:
        raise BankCardNotFound()
    return obj


# -------------------------------------------------------------
@router.post("/create", response_model=BankCardRead)
async def create_bank_card(*,
                           db: AsyncSession = Depends(deps.get_db),
                           current_user: User = Depends(
                               deps.get_current_user()),
                           bank_card_in: BankCardCreate,
                           background_tasks: BackgroundTasks):
    card_exist = await bank_card_crud.reab_by_bank_card_number(db=db, card_number=bank_card_in.card_number)
    if card_exist:
        raise BankCardDuplicate()
    bank_card_created = await bank_card_crud.create(db=db, obj_in=bank_card_in)
    background_tasks.add_task(verify_bank_card,)

# -------------------------------------------------------------


@router.delete("/delete/{bank_card_id}", response_model=BankCardRead)
async def delete_bank_card(*,
                           db: AsyncSession = Depends(deps.get_db),
                           current_user: User = Depends(deps.get_current_user()),
                           bank_card_id:UUID):
    bank_card_exist = await bank_card_crud.read_user_bank_card(db=db,user_id=current_user.id,card_id=bank_card_id)
    if not bank_card_exist:
        raise BankCardNotFound()
    bank_card_crud.delete(db=db,item_id=bank_card_id)
    return bank_card_exist
