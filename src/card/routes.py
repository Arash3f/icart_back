from datetime import datetime, timedelta
from random import randint
from fastapi import APIRouter, Depends
from pytz import timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import or_

from src import deps
from src.auth.exception import AccessDeniedException
from src.card.crud import card as card_crud, CardValueType
from src.card.exception import CardNotFoundException, CardPasswordInValidException
from src.log.models import LogType
from src.transaction.schema import TransactionCreate, TransactionRowCreate
from src.user.crud import user as user_crud
from src.log.crud import log as log_crud
from src.wallet.crud import wallet as wallet_crud
from src.cash.crud import cash as cash_crud, CashField, TypeOperation
from src.important_data.crud import important_data as important_data_crud
from src.transaction.crud import transaction as transaction_crud
from src.transaction.crud import transaction_row as transaction_row_crud
from src.card.models import Card, CardEnum
from src.card.schema import (
    CardDynamicPasswordInput,
    CardRead,
    CardUpdatePassword,
    CardFilter,
    CardFilterOrderFild,
    BuyCardResponse,
    CardForgetPasswordInput,
    CardToCardInput,
    ConfirmCardReceive,
)
from src.core.config import settings
from src.core.security import hash_password, pwd_context, verify_password
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
    TransactionValueType,
    TransactionReasonEnum,
    TransactionRow,
    TransactionStatusEnum,
)
from src.user.models import User
from src.utils.card_number import (
    generate_card_number,
    CardType,
    CreditType,
    CompanyType,
)
from src.wallet.exception import LackOfMoneyException, LockWalletException
from src.wallet.models import Wallet

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/card", tags=["card"])


# ---------------------------------------------------------------------------
@router.post("/buy/blue", response_model=BuyCardResponse)
async def buy_card(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> BuyCardResponse:
    # todo: set validation for type card
    # * Verify card existence with this type
    await card_crud.verify_existence_with_type(
        db=db,
        user=current_user,
        card_type=CardEnum.BLUE,
        is_active=True,
    )

    admin_user = await user_crud.verify_existence_by_username(
        db=db,
        username=settings.ADMIN_USERNAME,
    )
    receiver_card = await card_crud.get_active_card(
        db=db,
        card_value_type=CardValueType.CASH,
        wallet=admin_user.wallet,
    )

    # * Check user cash credit
    buy_cost = await important_data_crud.get_blue_card_cost(db=db)
    if current_user.cash.balance < buy_cost:
        raise LackOfMoneyException()

    # * Generate card number
    card_number = await generate_card_number(
        db=db,
        card_type=CardType.Swipe,
        credit_type=CreditType.Rial,
        company_type=CompanyType.Icart,
    )

    # ? Generate Card
    expiration_at = datetime.now(timezone("Asia/Tehran")) + timedelta(
        days=360,
    )
    card_password = randint(1000, 9999)
    card = Card(
        number=card_number,
        cvv2=randint(100, 999),
        type=CardEnum.BLUE,
        password=hash_password(str(card_password)),
        wallet_id=current_user.wallet.id,
    )
    card.expiration_at = expiration_at
    db.add(card)
    await db.commit()
    await db.refresh(card)

    # ? Generate transaction
    transaction = TransactionCreate(
        value=buy_cost,
        text="خرید کارت {}".format(card_number),
        value_type=TransactionValueType.CASH,
        receiver_id=receiver_card.id,
        transferor_id=card.id,
        code=await transaction_crud.generate_code(db=db),
        status=TransactionStatusEnum.ACCEPTED,
        reason=TransactionReasonEnum.PURCHASE,
    )
    main_tr = await transaction_crud.create(db=db, obj_in=transaction)
    transaction_row = TransactionRowCreate(
        transaction_id=main_tr.id,
        value=buy_cost,
        text="خرید کارت {}".format(card_number),
        value_type=TransactionValueType.CASH,
        receiver_id=receiver_card.id,
        transferor_id=card.id,
        code=await transaction_crud.generate_code(db=db),
        status=TransactionStatusEnum.ACCEPTED,
        reason=TransactionReasonEnum.PURCHASE,
    )
    await transaction_row_crud.create(db=db, obj_in=transaction_row)

    await cash_crud.update_cash_by_user(
        db=db,
        user=current_user,
        amount=buy_cost,
        cash_field=CashField.BALANCE,
        type_operation=TypeOperation.DECREASE,
    )
    await cash_crud.update_cash_by_user(
        db=db,
        user=admin_user,
        amount=buy_cost,
        cash_field=CashField.BALANCE,
        type_operation=TypeOperation.INCREASE,
    )

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.BUY_CARD,
        user_id=current_user.id,
        detail="کارت با شماره {} با موفقیت توسط کاربر {} خریداری شد".format(
            card.number,
            current_user.username,
        ),
    )

    # todo: Send SMS
    await db.commit()
    return BuyCardResponse(card_number=card_number, password=str(card_password))


# ---------------------------------------------------------------------------
@router.post("/confirm", response_model=ResultResponse)
async def confirm_card(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    confirm_data: ConfirmCardReceive,
) -> ResultResponse:
    # * Verify card existence with this type
    card = await card_crud.verify_by_number(
        db=db,
        number=confirm_data.card_number,
    )

    if card.wallet_id != current_user.wallet.id or card.is_active == False:
        raise CardNotFoundException()

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.BUY_CARD,
        user_id=current_user.id,
        detail="کارت با شماره {} با موفقیت توسط کاربر {} دریافت شد".format(
            card.number,
            current_user.username,
        ),
    )

    card.is_receive == True
    db.add(card)
    await db.commit()
    return ResultResponse(result="Success")


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
    # * Verify forget password
    verify_pass = verify_password(
        update_data.data.forget_password,
        obj_current.forget_password,
    )
    if not verify_pass:
        raise InCorrectDataException()
    # * verify new password
    if update_data.data.new_password != update_data.data.re_password:
        raise InCorrectDataException()
    # * Update card
    obj_current.password = hash_password(update_data.data.new_password)

    db.add(obj_current)
    await db.commit()

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
    filter_data.name = (
        or_(
            User.first_name.contains(filter_data.name),
            User.last_name.contains(filter_data.name),
        )
        if filter_data.name is not None
        else True
    )
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code is not None
        else True
    )
    filter_data.number = (
        (Card.number.contains(filter_data.number)) if filter_data.number else True
    )
    filter_data.type = (Card.type == filter_data.type) if filter_data.type else True
    filter_data.user_id = (
        (User.id == filter_data.user_id) if filter_data.user_id else True
    )

    # * Add filter fields
    query = (
        select(Card)
        .filter(
            and_(
                filter_data.name,
                filter_data.national_code,
                filter_data.number,
                filter_data.type,
                filter_data.user_id,
            ),
        )
        .join(Card.wallet)
        .join(Wallet.user)
        .order_by(Card.created_at.desc())
    )

    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == CardFilterOrderFild.number:
                query = query.order_by(Card.number.desc())
            elif field == CardFilterOrderFild.created_at:
                query = query.order_by(Card.created_at.desc())
            elif field == CardFilterOrderFild.updated_at:
                query = query.order_by(Card.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == CardFilterOrderFild.number:
                query = query.order_by(Card.number.asc())
            elif field == CardFilterOrderFild.created_at:
                query = query.order_by(Card.created_at.asc())
            elif field == CardFilterOrderFild.updated_at:
                query = query.order_by(Card.updated_at.asc())

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
@router.post(path="/forget_password/request", response_model=ResultResponse)
async def get_dynamic_password(
    *,
    db: object = Depends(deps.get_db),
    input_data: CardForgetPasswordInput,
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
    # ? Generate forget password
    forget_password = randint(100000, 999999)
    # ? Update card forget password
    card.forget_password = hash_password(str(forget_password))
    card.forget_password_exp = datetime.now(timezone("Asia/Tehran")) + timedelta(
        minutes=settings.DYNAMIC_PASSWORD_EXPIRE_MINUTES,
    )
    # ? Send SMS message
    # todo: complete sms server for send sms

    db.add(card)
    await db.commit()
    return ResultResponse(result="Forget Password Send Successfully")


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
        select(TransactionRow.value_type, func.sum(TransactionRow.value))
        .select_from(TransactionRow)
        .filter(
            and_(
                TransactionRow.transferor.mapper.class_.wallet_id
                == current_user.wallet.id,
                TransactionRow.created_at >= start,
            ),
        )
        .group_by(TransactionRow.value_type)
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
            select(TransactionRow.value_type, func.sum(TransactionRow.value))
            .select_from(TransactionRow)
            .filter(
                and_(
                    TransactionRow.transferor.mapper.class_.wallet_id
                    == current_user.wallet.id,
                    TransactionRow.created_at >= duration.start_date,
                    TransactionRow.created_at < duration.end_date,
                ),
            )
            .group_by(TransactionRow.value_type)
        )
        if current_user.role.name == "پذیرنده":
            query = query.filter(
                TransactionRow.reason != TransactionReasonEnum.PROFIT,
            )
        else:
            query = query.filter(
                TransactionRow.reason != TransactionReasonEnum.CONTRACT,
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


# # ---------------------------------------------------------------------------
# ? Note: Completed
# @router.post("/card_to_card", response_model=ResultResponse)
# async def card_to_card(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     current_user: User = Depends(deps.get_current_user()),
#     data: CardToCardInput,
# ) -> ResultResponse:
#     # * Verify card existence for this user
#     transferor_card = await card_crud.verify_by_number(
#         db=db,
#         number=data.transferor_card_number,
#     )
#     receiver_card = await card_crud.verify_by_number(
#         db=db,
#         number=data.receiver_card_number,
#     )
#     receiver_user = await wallet_crud.verify_existence(
#         db=db,
#         wallet_id=receiver_card.wallet_id,
#     )
#     if (
#         transferor_card.wallet != current_user.wallet
#         or transferor_card.type != CardEnum.CREDIT
#     ):
#         raise CardNotFoundException()
#     # * Verify Card exp
#     await card_crud.check_card_exp(db=db, card_id=transferor_card.id)
#
#     verify_pass = verify_password(
#         data.dynamic_password,
#         transferor_card.dynamic_password,
#     )
#     if not verify_pass:
#         raise CardPasswordInValidException()
#
#     if transferor_card.wallet.is_lock:
#         raise LockWalletException()
#
#     # * Check user cash credit
#     if current_user.cash.balance < data.amount:
#         raise LackOfMoneyException()
#
#     await cash_crud.update_cash_by_user(
#         db=db,
#         user=current_user,
#         amount=data.amount,
#         cash_field=CashField.BALANCE,
#         type_operation=TypeOperation.DECREASE,
#     )
#     await cash_crud.update_cash_by_user(
#         db=db,
#         user=receiver_user,
#         amount=data.amount,
#         cash_field=CashField.BALANCE,
#         type_operation=TypeOperation.INCREASE,
#     )
#
#     # ? Generate transaction
#     transaction = TransactionCreate(
#         value=data.amount,
#         text="عملیات انتقال پوا از {} به {}".format(
#             transferor_card.number,
#             receiver_card.number,
#         ),
#         value_type=TransactionValueType.CASH,
#         receiver_id=receiver_card.wallet_id,
#         transferor_id=transferor_card.wallet_id,
#         code=await transaction_crud.generate_code(db=db),
#         status=TransactionStatusEnum.ACCEPTED,
#         reason=TransactionReasonEnum.CARD_TO_CARD,
#     )
#     main_tr = await transaction_crud.create(db=db, obj_in=transaction)
#     transaction_row = TransactionRowCreate(
#         transaction_id=main_tr.id,
#         value=data.amount,
#         text="عملیات انتقال پوا از {} به {}".format(
#             transferor_card.number,
#             receiver_card.number,
#         ),
#         value_type=TransactionValueType.CASH,
#         receiver_id=receiver_card.wallet_id,
#         transferor_id=transferor_card.wallet_id,
#         code=await transaction_crud.generate_code(db=db),
#         status=TransactionStatusEnum.ACCEPTED,
#         reason=TransactionReasonEnum.CARD_TO_CARD,
#     )
#     await transaction_row_crud.create(db=db, obj_in=transaction_row)
#
#     await db.commit()
#     return ResultResponse(result="Successful")
