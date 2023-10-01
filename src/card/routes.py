from datetime import datetime, timedelta
from random import randint

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.card.crud import card as card_crud
from src.card.models import Card
from src.card.schema import (
    CardDynamicPasswordInput,
    CardRead,
    CardUpdatePassword,
)
from src.core.config import settings
from src.core.security import hash_password, pwd_context
from src.exception import InCorrectDataException
from src.permission import permission_codes as permission
from src.schema import IDRequest, ResultResponse
from src.user.models import User
from src.utils.sms import send_dynamic_password_sms
from src.wallet.crud import wallet as wallet_crud

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/card", tags=["card"])


# ---------------------------------------------------------------------------
@router.put("/update_password", response_model=CardRead)
async def update_card(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    update_data: CardUpdatePassword,
) -> CardRead:
    """
    ! Update Card's password

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update password

    Returns
    -------
    card
        Updated card

    Raises
    ------
    InCorrectDataException
    CardNotFoundException
    """
    # * Verify card existence
    obj_current = await card_crud.verify_existence(db=db, card_id=update_data.where.id)
    # * Verify old password
    verify = pwd_context.verify(update_data.data.password, obj_current.password)
    if not verify:
        raise InCorrectDataException()
    # * verify new password
    if update_data.data.new_password != update_data.data.re_password:
        raise InCorrectDataException()
    # * Update card
    update_data.data.password = hash_password(update_data.data.new_password)
    card = await card_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )

    return card


# ---------------------------------------------------------------------------
@router.get("/list", response_model=list[CardRead])
async def read_card_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_CARD]),
    ),
    skip: int = 0,
    limit: int = 10,
) -> list[CardRead]:
    """
    ! Read Card

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    skip
        Pagination skip
    limit
        Pagination limit

    Returns
    -------
    card_list
        List of card
    """
    card_list = await card_crud.get_multi(db=db, skip=skip, limit=limit)
    return card_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=CardRead)
async def find_card(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_CARD]),
    ),
    read_data: IDRequest,
) -> CardRead:
    """
    ! Find Card

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    read_data
        Target Card's ID

    Returns
    -------
    card
        Found Card

    Raises
    ------
    CardNotFoundException
    """
    # * Verify card existence
    card = await card_crud.verify_existence(db=db, card_id=read_data.id)
    return card


# ---------------------------------------------------------------------------
@router.get("/my", response_model=list[CardRead])
async def find_my_card(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> list[CardRead]:
    """
    ! Find Card

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User

    Returns
    -------
    card_list
        List of my card

    Raises
    ------
    WalletNotFoundException
    """
    # * Find user wallet
    wallet = await wallet_crud.find_by_user_id(db=db, user_id=current_user.id)
    # * Find All My Cards
    query = select(Card).where(Card.wallet_id == wallet.id)
    card_list = await card_crud.get_multi(db=db, query=query)
    return card_list


# ---------------------------------------------------------------------------
@router.post(path="/dynamic_password", response_model=ResultResponse)
async def get_dynamic_password(
    *,
    db: object = Depends(deps.get_db),
    input_data: CardDynamicPasswordInput,
) -> ResultResponse:
    """
    ! Get card dynamic password

    Parameters
    ----------
    db
        Target database connection
    input_data
        Card's number

    Returns
    -------
    response
        Card's dynamic password

    """
    # * Find Card
    card = await card_crud.verify_by_number(db=db, number=input_data.number)
    # ? Generate dynamic password
    dynamic_password = randint(100000, 999999)
    # ? Update wallet dynamic password
    card.dynamic_password = dynamic_password
    card.dynamic_password_exp = datetime.now() + timedelta(
        minutes=settings.DYNAMIC_PASSWORD_EXPIRE_MINUTES,
    )
    # ? Send SMS message
    # todo:
    send_dynamic_password_sms(
        dynamic_password=dynamic_password,
        phone_number=card.wallet.user.phone_number,
        exp_time=card.dynamic_password_exp,
    )

    db.add(card)
    await db.commit()
    return ResultResponse(result="Success")


# # ---------------------------------------------------------------------------
# Todo: Complete
# @router.post("/balance", response_model=BalanceRead)
# async def find_card(*,
#                     db: AsyncSession =
# Depends(deps.get_db),
#                     current_user: User =
# Depends(deps.get_current_user())) -> BalanceRead:
#     """
#     ! Read Card Balance
#
#     Parameters
#     ----------
#     db
#         Target database connection
#     current_user
#         Requester User
#
#     Returns
#     -------
#     card_list
#         List of my card
#     Raises
#     ------
#     WalletNotFoundException
#     """
#     # * Find user wallet
#     wallet = await wallet_crud.find_by_user_id(db=db, user_id=current_user.id)
#     # * Find All Cards
#     query = select(Card).where(Card.wallet_id == wallet.id)
#     card_list = await card_crud.get_multi(db=db, query=query)
#     return card_list
