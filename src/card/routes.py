from datetime import datetime, timedelta
from random import randint
from fastapi import APIRouter, Depends
from pytz import timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.auth.exception import AccessDeniedException
from src.card.crud import card as card_crud
from src.transaction.schema import TransactionCreate
from src.user.crud import user as user_crud
from src.cash.crud import cash as cash_crud
from src.transaction.crud import transaction as transaction_crud
from src.card.models import Card, CardEnum
from src.card.schema import (
    CardDynamicPasswordInput,
    CardRead,
    CardUpdatePassword,
    CardFilter,
    CardFilterOrderFild,
    BuyCard,
    CreateCard,
    BuyCardResponse,
)
from src.core.config import settings
from src.core.security import hash_password, pwd_context
from src.exception import InCorrectDataException
from src.permission import permission_codes as permission
from src.schema import (
    IDRequest,
    ResultResponse,
    VerifyUserDep,
    ChartFilterInput,
    Duration,
    ChartTypeResponse,
)
from src.transaction.models import (
    Transaction,
    TransactionValueType,
    TransactionReasonEnum,
)
from src.user.models import User
from src.utils.card_number import (
    generate_card_number,
    CardType,
    CreditType,
    CompanyType,
)
from src.wallet.exception import LackOfMoneyException

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/card", tags=["card"])


# # ---------------------------------------------------------------------------
# @router.post("/buy", response_model=BuyCardResponse)
# async def buy_card(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     current_user: User = Depends(deps.get_current_user()),
#     data_in: BuyCard,
# ) -> BuyCardResponse:
#     # * Verify card existence with this type
#     await card_crud.verify_existence_with_type(
#         db=db,
#         user=current_user,
#         card_type=data_in.type,
#     )
#     icart_user = await user_crud.find_by_username(
#         db=db,
#         username=settings.ADMIN_USERNAME,
#     )
#
#     # * Check user cash credit
#     # todo: update card amount
#     if current_user.cash.balance < 4900000:
#         raise LackOfMoneyException()
#
#     # ? Generate transaction
#     transaction = TransactionCreate(
#         value=float(4900000),
#         text="خرید کارت {}",
#         value_type=TransactionValueType.CASH,
#         receiver_id=icart_user.wallet.id,
#         transferor_id=current_user.wallet.id,
#         code=str(randint(100000000000, 999999999999)),
#         reason=TransactionReasonEnum.PURCHASE,
#     )
#     await transaction_crud.create(db=db, obj_in=transaction)
#
#     # * Generate card number
#     if data_in.type == CardEnum.CREDIT:
#         card_number = await generate_card_number(
#             db=db,
#             card_type=CardType.Credit,
#             credit_type=CreditType.Rial,
#             company_type=CompanyType.Icart,
#         )
#     else:
#         card_number = await generate_card_number(
#             db=db,
#             card_type=CardType.Swipe,
#             credit_type=CreditType.Rial,
#             company_type=CompanyType.Icart,
#         )
#
#     print(card_number)
#
#     # ? Generate Card
#     expiration_at = datetime.now(timezone("Asia/Tehran")) + timedelta(
#         days=360,
#     )
#     card_password = randint(1000, 9999)
#     card = Card(
#         number=card_number,
#         cvv2=randint(100, 999),
#         type=data_in.type,
#         password=hash_password(str(card_password)),
#         wallet_id=current_user.wallet.id,
#     )
#     card.expiration_at = expiration_at
#     db.add(card)
#
#     await cash_crud.decrease_cash_credit(db=db, user=current_user, amount=4900000)
#     await cash_crud.increase_cash_balance_by_user(db=db, user=icart_user, amount=4900000)
#     await cash_crud.(db=db, user=icart_user, amount=4900000)
#     await db.commit()
#     return BuyCardResponse(card_number=card_number, password=str(card_password))


# ---------------------------------------------------------------------------
@router.put("/update_password", response_model=ResultResponse)
async def update_card(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    update_data: CardUpdatePassword,
) -> ResultResponse:
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
    obj_current = await card_crud.verify_by_number(
        db=db,
        number=update_data.where.number,
    )
    # * Verify old password
    verify = pwd_context.verify(update_data.data.password, obj_current.password)
    if not verify:
        raise InCorrectDataException()
    # * verify new password
    if update_data.data.new_password != update_data.data.re_password:
        raise InCorrectDataException()
    # * Update card
    update_data.data.password = hash_password(update_data.data.new_password)
    await card_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )

    return ResultResponse(result="Password Updated Successfully")


# ---------------------------------------------------------------------------
@router.post("/list", response_model=list[CardRead])
async def read_card_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_CARD]),
    ),
    filter_data: CardFilter,
    skip: int = 0,
    limit: int = 10,
) -> list[CardRead]:
    """
    ! Read Card

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    skip
        Pagination skip
    limit
        Pagination limit
    filter_data
        Filter data

    Returns
    -------
    card_list
        List of card

    Raises
    ------
    UserNotFoundException
    """
    # * Prepare filter fields
    filter_data.number = (
        (Card.number.contains(filter_data.number)) if filter_data.number else True
    )
    filter_data.type = (Card.type == filter_data.type) if filter_data.type else True
    if filter_data.user_id:
        filter_user = await user_crud.verify_existence(
            db=db,
            user_id=filter_data.user_id,
        )
        filter_data.user_id = Card.wallet_id == filter_user.wallet.id
    else:
        filter_data.user_id = True

    # * Add filter fields
    query = select(Card).filter(
        and_(
            filter_data.number,
            filter_data.type,
            filter_data.user_id,
        ),
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == CardFilterOrderFild.number:
                query = query.order_by(Card.number.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == CardFilterOrderFild.number:
                query = query.order_by(Card.number.asc())

    # * Have permissions
    if not verify_data.is_valid:
        query.where(Card.wallet_id == verify_data.user.wallet.id)

    card_list = await card_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return card_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=CardRead)
async def find_card(
    *,
    db: AsyncSession = Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_TICKET]),
    ),
    read_data: IDRequest,
) -> CardRead:
    """
    ! Find Card

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
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
    # * Have permissions
    if verify_data.is_valid:
        card = await card_crud.verify_existence(db=db, card_id=read_data.id)
        return card

    else:
        card = await card_crud.verify_existence(db=db, card_id=read_data.id)
        if card.wallet == verify_data.user.wallet:
            return card
        else:
            raise AccessDeniedException()


# ---------------------------------------------------------------------------
@router.post(path="/dynamic_password/request", response_model=ResultResponse)
async def get_dynamic_password(
    *,
    db: object = Depends(deps.get_db),
    input_data: CardDynamicPasswordInput,
) -> ResultResponse:
    """
    ! Request for dynamic password

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

    Raises
    ------
    CardNotFoundException
    """
    # * Find Card
    card = await card_crud.verify_by_number(db=db, number=input_data.number)
    # ? Generate dynamic password
    dynamic_password = randint(100000, 999999)
    # ? Update wallet dynamic password
    card.dynamic_password = hash_password(str(dynamic_password))
    card.dynamic_password_exp = datetime.now(timezone("Asia/Tehran")) + timedelta(
        minutes=settings.DYNAMIC_PASSWORD_EXPIRE_MINUTES,
    )
    # ? Send SMS message
    # todo: complete sms server for send sms

    db.add(card)
    await db.commit()
    return ResultResponse(result="Dynamic Password Send Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/manage/chart", response_model=list[ChartTypeResponse])
async def get_manage_chart(
    *,
    db: object = Depends(deps.get_db),
    filter_data: ChartFilterInput,
    current_user: User = Depends(deps.get_current_user()),
) -> list[ChartTypeResponse]:
    """
    ! Manage Card Data On Chart

    Parameters
    ----------
    db
        Target database connection
    filter_data
        filter data for customize response
    current_user
        Requester User

    Returns
    -------
    chart_data
        final chart data
    """
    start = filter_data.duration.start_date
    end = filter_data.duration.end_date
    unit = filter_data.unit

    chart_data: list[ChartTypeResponse] = []

    # ? calculate durations
    buf_time = start
    buf_cash = current_user.cash.balance
    buf_credit = current_user.credit.balance

    query = (
        select(Transaction.value_type, func.sum(Transaction.value))
        .select_from(Transaction)
        .filter(
            and_(
                Transaction.transferor_id == current_user.wallet.id,
                Transaction.created_at >= start,
            ),
        )
        .group_by(Transaction.value_type)
    )
    res = await db.execute(
        query,
    )
    buf_data_list = res.all()
    for data in buf_data_list:
        if data[0].value == "CASH":
            buf_cash -= data[1]
        else:
            buf_credit -= data[1]

    while buf_time < end:
        buf_end = buf_time + timedelta(
            days=unit,
        )
        duration = Duration(
            start_date=buf_time,
            end_date=buf_end,
        )

        query = (
            select(Transaction.value_type, func.sum(Transaction.value))
            .select_from(Transaction)
            .filter(
                and_(
                    Transaction.transferor_id == current_user.wallet.id,
                    Transaction.created_at >= duration.start_date,
                    Transaction.created_at < duration.end_date,
                ),
            )
            .group_by(Transaction.value_type)
        )
        response = await db.execute(
            query,
        )
        data_list = response.all()
        cash_obj = ChartTypeResponse(
            duration=duration,
            type="CASH",
            value=0,
        )
        credit_obj = ChartTypeResponse(
            duration=duration,
            type="CREDIT",
            value=0,
        )
        for data in data_list:
            if data[0].value == "CASH":
                buf_cash += data[1]
                cash_obj.value += data[1]
            else:
                buf_credit += data[1]
                credit_obj.value += data[1]

        chart_data.append(credit_obj)
        chart_data.append(cash_obj)

        buf_time = buf_end
    return chart_data
