from random import randint

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

import jdatetime
from src import deps
from src.auth.exception import (
    IncorrectUsernameOrPasswordException,
    InactiveUserException,
)
from src.card.exception import CardNotFoundException, CardPasswordInValidException
from src.core.config import settings
from src.core.security import verify_password
from src.exception import InCorrectDataException
from src.fee.models import Fee, FeeTypeEnum, FeeUserType
from src.installments.schema import InstallmentsCreate
from src.log.models import LogType
from src.merchant.crud import merchant as merchant_crud
from src.card.crud import card as card_crud
from src.merchant.models import Merchant
from src.transaction.exception import TransactionLimitException
from src.wallet.crud import wallet as wallet_crud
from src.merchant.exception import MerchantNotFoundException
from src.permission import permission_codes as permission
from src.pos.crud import pos as pos_crud
from src.transaction.models import (
    TransactionValueType,
    TransactionReasonEnum,
    TransactionStatusEnum,
)
from src.transaction.schema import TransactionCreate, TransactionRowCreate
from src.user.crud import user as user_crud
from src.log.crud import log as log_crud
from src.fee.crud import fee as fee_crud
from src.auth.crud import auth as auth_crud
from src.cash.crud import cash as cash_crud, CashField, TypeOperation
from src.credit.crud import credit as credit_crud, CreditField
from src.transaction.crud import transaction_row as transaction_row_crud
from src.transaction.crud import transaction as transaction_crud
from src.pos.exception import PosNotFoundException
from src.pos.models import Pos
from src.pos.schema import (
    PosBase,
    PosCreate,
    PosRead,
    PosUpdate,
    PosFilter,
    ConfigPosInput,
    BalanceOutput,
    BalanceInput,
    PurchaseInput,
    PurchaseOutput,
    PosPurchaseType,
    ConfigurationPosInput,
    ConfigurationPosOutput,
    InstallmentsPurchaseOutput,
    InstallmentsPurchaseInput,
    CardBalanceType,
    PosFilterOrderFild,
)
from src.schema import DeleteResponse, IDRequest
from src.user.models import User
from src.wallet.exception import (
    LackOfMoneyException,
    LackOfCreditException,
    LockWalletException,
    MerchantLackOfMoneyException,
)

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/pos", tags=["pos"])


# ---------------------------------------------------------------------------
@router.delete("/delete", response_model=DeleteResponse)
async def delete_pos(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.DELETE_POS]),
    ),
    delete_data: IDRequest,
) -> DeleteResponse:
    """
    ! Delete Pos

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    delete_data
        Necessary data for delete pos

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    PosNotFoundException
    """
    # * Verify pos existence
    pos = await pos_crud.verify_existence(db=db, pos_id=delete_data.id)
    # * Delete Pos
    await pos_crud.delete(db=db, item_id=delete_data.id)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.UPDATE_POS,
        user_id=current_user.id,
        detail="پوز با شماره {} با موفقیت توسط کاربر {} حذف شد".format(
            pos.number,
            current_user.username,
        ),
    )

    return DeleteResponse(result="Pos Deleted Successfully")


# ---------------------------------------------------------------------------
@router.post("/create", response_model=PosBase)
async def create_pos(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CREATE_POS]),
    ),
    create_data: PosCreate,
) -> PosBase:
    """
    ! Create Pos

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    create_data
        Necessary data for create pos

    Returns
    -------
    pos
        New pos

    Raises
    ------
    PosTokenIsDuplicatedException
    MerchantNotFoundException
    """
    # * Verify merchant existence
    await merchant_crud.verify_existence(db=db, merchant_id=create_data.merchant_id)
    # * Verify pos Token duplicated
    await pos_crud.verify_duplicate_number(db=db, number=create_data.number)
    # * Create Pos
    pos = await pos_crud.create(db=db, obj_in=create_data)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.UPDATE_POS,
        user_id=current_user.id,
        detail="پوز با شماره {} با موفقیت توسط کاربر {} ایجاد شد".format(
            pos.number,
            current_user.username,
        ),
    )

    return pos


# ---------------------------------------------------------------------------
@router.put("/update", response_model=PosRead)
async def update_pos(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_POS]),
    ),
    update_data: PosUpdate,
) -> PosRead:
    """
    ! Update Pos

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update pos

    Returns
    -------
    pos
        Updated pos

    Raises
    ------
    PosNotFoundException
    PosTokenIsDuplicatedException
    MerchantNotFoundException
    """
    # * Verify merchant existence
    await merchant_crud.verify_existence(
        db=db,
        merchant_id=update_data.data.merchant_id,
    )
    # * Verify pos existence
    obj_current = await pos_crud.verify_existence(db=db, pos_id=update_data.where.id)
    # * Verify pos number duplicate
    await pos_crud.verify_duplicate_number(db=db, number=update_data.data.number)
    # * Update pos
    pos = await pos_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.UPDATE_POS,
        user_id=current_user.id,
        detail="پوز با شماره {} با موفقیت توسط کاربر {} ویرایش شد".format(
            pos.number,
            current_user.username,
        ),
    )

    return pos


# ---------------------------------------------------------------------------
@router.post("/list", response_model=list[PosRead])
async def read_pos_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_POS]),
    ),
    skip: int = 0,
    limit: int = 10,
    filter_data: PosFilter,
) -> list[PosRead]:
    """
    ! Read Pos

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
    filter_data
        Filter data

    Returns
    -------
    pos_list
        List of pos
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
    filter_data.merchant_id = (
        (Pos.merchant_id == filter_data.merchant_id)
        if filter_data.merchant_id is not None
        else True
    )
    filter_data.number = (
        (Pos.number.contains(filter_data.number))
        if filter_data.number is not None
        else True
    )
    filter_data.merchant_number = (
        (Merchant.number.contains(filter_data.merchant_number))
        if filter_data.merchant_number is not None
        else True
    )
    # * Add filter fields
    query = (
        select(Pos)
        .filter(
            and_(
                filter_data.name,
                filter_data.national_code,
                filter_data.merchant_id,
                filter_data.number,
                filter_data.merchant_number,
            ),
        )
        .join(Pos.merchant)
        .join(Merchant.user)
    ).order_by(Pos.created_at.desc())
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == PosFilterOrderFild.number:
                query = query.order_by(Pos.number.desc())
            elif field == PosFilterOrderFild.created_at:
                query = query.order_by(Pos.created_at.desc())
            elif field == PosFilterOrderFild.updated_at:
                query = query.order_by(Pos.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == PosFilterOrderFild.number:
                query = query.order_by(Pos.number.asc())
            elif field == PosFilterOrderFild.created_at:
                query = query.order_by(Pos.created_at.asc())
            elif field == PosFilterOrderFild.updated_at:
                query = query.order_by(Pos.updated_at.asc())
    pos_list = await pos_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return pos_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=PosRead)
async def find_pos(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_POS]),
    ),
    read_data: IDRequest,
) -> PosRead:
    """
    ! Find Pos

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    read_data
        Target Pos's ID

    Returns
    -------
    pos
        Found Pos

    Raises
    ------
    PosNotFoundException
    """
    # * Verify pos existence
    pos = await pos_crud.verify_existence(db=db, pos_id=read_data.id)
    return pos


# ---------------------------------------------------------------------------
@router.post("/config", response_model=ConfigurationPosOutput)
async def config(
    *,
    db: AsyncSession = Depends(deps.get_db),
    config_data: ConfigPosInput,
) -> ConfigurationPosOutput:
    """
    ! Config Pos

    Parameters
    ----------
    db
        Target database connection
    config_data
        Necessary data for config pos

    Returns
    -------
    res
        result of configuration

    Raises
    ------
    PosNotFoundException
    """
    # * Verify pos existence
    pos = await pos_crud.find_by_number(db=db, number=config_data.terminal_number)

    if pos.merchant.number != config_data.merchant_number:
        raise PosNotFoundException(time=str(jdatetime.datetime.now()))

    return ConfigurationPosOutput(
        merchant_name=pos.merchant.contract.name,
        tel=pos.merchant.user.phone_number,
    )


# ---------------------------------------------------------------------------
@router.post("/configuration", response_model=ConfigurationPosOutput)
async def config(
    *,
    db: AsyncSession = Depends(deps.get_db),
    config_data: ConfigurationPosInput,
) -> ConfigurationPosOutput:
    """
    ! Config Pos

    Parameters
    ----------
    db
        Target database connection
    config_data
        Necessary data for config pos

    Returns
    -------
    res
        result of configuration

    Raises
    ------
    IncorrectUsernameOrPasswordException
    InactiveUserException
    PosNotFoundException
    """
    pos = await pos_crud.find_by_number(db=db, number=config_data.terminal_number)

    user = await auth_crud.authenticate(
        db=db,
        username=pos.merchant.user.username,
        password=config_data.password,
    )
    if not user:
        raise IncorrectUsernameOrPasswordException()
    elif not user.is_active:
        raise InactiveUserException()

    return ConfigurationPosOutput(
        merchant_name=pos.merchant.contract.name,
        tel=pos.merchant.user.phone_number,
    )


# ---------------------------------------------------------------------------
@router.post("/balance", response_model=BalanceOutput)
async def balance(
    *,
    db: AsyncSession = Depends(deps.get_db),
    card_data: BalanceInput,
) -> BalanceOutput:
    """
    ! Config Pos

    Parameters
    ----------
    db
        Target database connection
    card_data
        Necessary data for balance card

    Returns
    -------
    res
        card amount

    Raises
    ------
    PosNotFoundException
    CardNotFoundException
    """
    c_time = str(jdatetime.datetime.now())

    # * Verify pos existence
    pos = await pos_crud.find_by_number(db=db, number=card_data.terminal_number)

    if pos.merchant.number != card_data.merchant_number:
        raise PosNotFoundException()

    # * Verify Card number existence
    card = await card_crud.verify_by_number(db=db, number=card_data.card_track)

    # * Verify Card password
    verify_pass = verify_password(card_data.password, card.password)
    if not verify_pass:
        raise CardPasswordInValidException()

    cash_balance = card.wallet.user.cash.balance
    cash_balance += card.wallet.user.cash.cash_back
    credit_balance = card.wallet.user.credit.balance

    response = BalanceOutput(
        cash_balance=cash_balance,
        credit_balance=credit_balance,
        traction_code=randint(100000, 999999),
        date_time=str(jdatetime.datetime.now()),
    )
    return response


# ---------------------------------------------------------------------------
@router.post("/purchase", response_model=PurchaseOutput)
async def purchase(
    *,
    db: AsyncSession = Depends(deps.get_db),
    input_data: PurchaseInput,
) -> PurchaseOutput:
    """
    ! purchase request

    Parameters
    ----------
    db
        Target database connection
    input_data
        Necessary data for purchase

    Returns
    -------
    res
        result of operation

    Raises
    ------
    PosNotFoundException
    CardNotFoundException
    """
    c_time = str(jdatetime.datetime.now())
    # * Verify pos existence
    pos = await pos_crud.find_by_number(db=db, number=input_data.terminal_number)
    # * Verify merchant number
    if pos.merchant.number != input_data.merchant_number:
        raise MerchantNotFoundException()
    # * Verify Card number existence
    card = await card_crud.verify_by_number(db=db, number=input_data.card_track)
    # * Verify Card exp
    await card_crud.check_card_exp(db=db, card_id=card.id)
    # * Verify Card password
    verify_pass = verify_password(input_data.password, card.password)
    if not verify_pass:
        raise CardPasswordInValidException()

    if card.wallet.is_lock:
        raise LockWalletException()

    # ! Transaction ceiling
    user_transactions_amount = (
        await transaction_row_crud.calculate_user_amount_transaction(
            db=db,
            user=card.wallet.user,
            min=44640,
        )
    )
    if user_transactions_amount >= 400000000:
        raise TransactionLimitException()

    # * Find All users
    agent = pos.merchant.agent
    merchant = pos.merchant
    icart_user = await user_crud.find_by_username(
        db=db,
        username=settings.ADMIN_USERNAME,
    )
    # * Calculate cashback for requester card with merchant
    find_cash_back = merchant_crud.calculate_user_cash_back(
        db=db,
        merchant=merchant,
        card=card,
    )
    cash_back = (input_data.amount * find_cash_back) / 100
    # * Calculate all users profit and cost
    merchant_profit = (input_data.amount * (100 - merchant.profit_rate)) / 100
    contract_amount = input_data.amount - merchant_profit
    new_amount = contract_amount - cash_back

    # ! Agent
    agent_profit = (new_amount * agent.profit_rate) / 100
    icart_profit = new_amount - agent_profit

    # * Calculate Fee
    if input_data.type == PosPurchaseType.DIRECT:
        fee_type = FeeTypeEnum.CASH
    elif input_data.type == PosPurchaseType.CREDIT:
        fee_type = FeeTypeEnum.CREDIT
    else:
        raise InCorrectDataException()

    user_fee = await fee_crud.calculate_fee(
        db=db,
        amount=input_data.amount,
        value_type=fee_type,
        user_type=FeeUserType.USER,
    )
    merchant_fee = await fee_crud.calculate_fee(
        db=db,
        amount=input_data.amount,
        value_type=fee_type,
        user_type=FeeUserType.MERCHANT,
    )

    requester_user = card.wallet.user
    merchant_user = pos.merchant.user

    if input_data.type == PosPurchaseType.DIRECT:
        if (
            merchant_user.cash.balance < merchant_fee
            and input_data.amount < merchant_fee
        ):
            raise MerchantLackOfMoneyException()
    elif input_data.type == PosPurchaseType.CREDIT:
        if merchant_user.cash.balance < merchant_fee:
            raise MerchantLackOfMoneyException()
    else:
        raise LackOfMoneyException()

    if requester_user.cash.balance < user_fee:
        raise LackOfMoneyException()
    if (
        input_data.type == PosPurchaseType.DIRECT
        and requester_user.cash.balance < input_data.amount + user_fee
    ):
        raise LackOfMoneyException()
    if (
        input_data.type == PosPurchaseType.CREDIT
        and requester_user.credit.balance < input_data.amount
    ):
        raise LackOfCreditException()

    # ! Transactions
    # ? lock user wallet
    user_wallet = await wallet_crud.verify_by_user_id(db=db, user_id=requester_user.id)
    user_wallet.is_lock = True
    db.add(user_wallet)
    # ? lock merchant wallet
    merchant_wallet = await wallet_crud.verify_by_user_id(
        db=db,
        user_id=merchant_user.id,
    )
    merchant_wallet.is_lock = True
    db.add(merchant_wallet)
    await db.commit()

    # ! Main
    main_code = await transaction_crud.generate_code(db=db)
    main_tr = TransactionCreate(
        status=TransactionStatusEnum.ACCEPTED,
        value=float(input_data.amount),
        text="عملیات خرید از فروشنده {}".format(merchant.contract.name),
        value_type=TransactionValueType.CASH,
        receiver_id=merchant.user.wallet.id,
        transferor_id=card.wallet.id,
        code=main_code,
        reason=TransactionReasonEnum.PURCHASE,
    )
    main_tr = await transaction_crud.create(db=db, obj_in=main_tr)

    # ! Merchant Fee
    merchant_user.cash.balance = merchant.user.cash.balance - merchant_fee
    await cash_crud.update_cash_by_user(
        db=db,
        user=icart_user,
        amount=merchant_fee,
        cash_field=CashField.BALANCE,
        type_operation=TypeOperation.INCREASE,
    )
    merchant_fee_tr = TransactionRowCreate(
        transaction_id=main_tr.id,
        status=TransactionStatusEnum.ACCEPTED,
        value=float(merchant_fee),
        text="کارمزد تراکنش",
        value_type=TransactionValueType.CASH,
        receiver_id=icart_user.wallet.id,
        transferor_id=merchant_user.wallet.id,
        code=await transaction_crud.generate_code(db=db),
        reason=TransactionReasonEnum.FEE,
    )
    await transaction_row_crud.create(db=db, obj_in=merchant_fee_tr)

    # ! User Fee
    requester_user.cash.balance = requester_user.cash.balance - user_fee
    await cash_crud.update_cash_by_user(
        db=db,
        user=icart_user,
        amount=user_fee,
        cash_field=CashField.BALANCE,
        type_operation=TypeOperation.INCREASE,
    )
    user_fee_tr = TransactionRowCreate(
        transaction_id=main_tr.id,
        status=TransactionStatusEnum.ACCEPTED,
        value=float(user_fee),
        text="کارمزد تراکنش",
        value_type=TransactionValueType.CASH,
        receiver_id=icart_user.wallet.id,
        transferor_id=card.wallet.id,
        code=await transaction_crud.generate_code(db=db),
        reason=TransactionReasonEnum.FEE,
    )
    await transaction_row_crud.create(db=db, obj_in=user_fee_tr)

    # ! Profit and cost
    if input_data.type == PosPurchaseType.DIRECT:
        cost = input_data.amount - requester_user.cash.cash_back
        cost_cash_back = input_data.amount - cost
        await cash_crud.update_cash_by_user(
            db=db,
            user=requester_user,
            amount=cost,
            cash_field=CashField.BALANCE,
            type_operation=TypeOperation.DECREASE,
        )
        await cash_crud.update_cash_by_user(
            db=db,
            user=requester_user,
            amount=cost_cash_back,
            cash_field=CashField.CASH_BACK,
            type_operation=TypeOperation.DECREASE,
        )
        await cash_crud.update_cash_by_user(
            db=db,
            user=merchant_user,
            amount=merchant_profit,
            cash_field=CashField.BALANCE,
            type_operation=TypeOperation.INCREASE,
        )
        sub_main_tr = TransactionRowCreate(
            transaction_id=main_tr.id,
            status=TransactionStatusEnum.ACCEPTED,
            value=float(input_data.amount),
            text="عملیات خرید از فروشنده {}".format(merchant.contract.name),
            value_type=TransactionValueType.CASH,
            receiver_id=merchant.user.wallet.id,
            transferor_id=card.wallet.id,
            code=await transaction_crud.generate_code(db=db),
            reason=TransactionReasonEnum.PURCHASE,
        )
        await transaction_row_crud.create(db=db, obj_in=sub_main_tr)

        if agent.parent:
            agent_parent_profit = (agent_profit * agent.parent.profit_rate) / 100
            await cash_crud.update_cash_by_user(
                db=db,
                user=agent.parent.user,
                amount=agent_parent_profit,
                cash_field=CashField.BALANCE,
                type_operation=TypeOperation.INCREASE,
            )
            agent_tr = TransactionRowCreate(
                transaction_id=main_tr.id,
                status=TransactionStatusEnum.ACCEPTED,
                value=float(agent_parent_profit),
                text="سود از فروشنده {}".format(merchant.contract.name),
                value_type=TransactionValueType.CASH,
                receiver_id=agent.parent.user.wallet.id,
                transferor_id=merchant.user.wallet.id,
                code=await transaction_crud.generate_code(db=db),
                reason=TransactionReasonEnum.PROFIT,
            )
            await transaction_row_crud.create(db=db, obj_in=agent_tr)
            agent_profit -= agent_parent_profit
        await cash_crud.update_cash_by_user(
            db=db,
            user=agent.user,
            amount=agent_profit,
            cash_field=CashField.BALANCE,
            type_operation=TypeOperation.INCREASE,
        )
        agent_tr = TransactionRowCreate(
            transaction_id=main_tr.id,
            status=TransactionStatusEnum.ACCEPTED,
            value=float(agent_profit),
            text="سود از فروشنده {}".format(merchant.contract.name),
            value_type=TransactionValueType.CASH,
            receiver_id=agent.user.wallet.id,
            transferor_id=merchant.user.wallet.id,
            code=await transaction_crud.generate_code(db=db),
            reason=TransactionReasonEnum.PROFIT,
        )
        await transaction_row_crud.create(db=db, obj_in=agent_tr)

        await cash_crud.update_cash_by_user(
            db=db,
            user=icart_user,
            amount=icart_profit,
            cash_field=CashField.BALANCE,
            type_operation=TypeOperation.INCREASE,
        )
        icart_tr = TransactionRowCreate(
            transaction_id=main_tr.id,
            status=TransactionStatusEnum.ACCEPTED,
            value=float(icart_profit),
            text="سود از فروشنده {}".format(merchant.contract.name),
            value_type=TransactionValueType.CASH,
            receiver_id=icart_user.wallet.id,
            transferor_id=merchant.user.wallet.id,
            code=await transaction_crud.generate_code(db=db),
            reason=TransactionReasonEnum.PROFIT,
        )
        await transaction_row_crud.create(db=db, obj_in=icart_tr)
        contract_tr = TransactionRowCreate(
            transaction_id=main_tr.id,
            status=TransactionStatusEnum.ACCEPTED,
            value=float(contract_amount),
            text="برداشت سود خدمات",
            value_type=TransactionValueType.CASH,
            receiver_id=icart_user.wallet.id,
            transferor_id=merchant.user.wallet.id,
            code=await transaction_crud.generate_code(db=db),
            reason=TransactionReasonEnum.CONTRACT,
        )
        await transaction_row_crud.create(db=db, obj_in=contract_tr)
        # ! Cash Back
        await cash_crud.update_cash_by_user(
            db=db,
            user=requester_user,
            amount=cash_back,
            cash_field=CashField.CASH_BACK,
            type_operation=TypeOperation.INCREASE,
        )
        cash_back_tr = TransactionRowCreate(
            transaction_id=main_tr.id,
            status=TransactionStatusEnum.ACCEPTED,
            value=float(cash_back),
            text="کش بک شما بابت خرید از فروشنده {}".format(merchant.contract.name),
            value_type=TransactionValueType.CASH,
            receiver_id=card.wallet.id,
            transferor_id=icart_user.wallet.id,
            code=await transaction_crud.generate_code(db=db),
            reason=TransactionReasonEnum.CASH_BACK,
        )
        await transaction_row_crud.create(db=db, obj_in=cash_back_tr)
    else:
        cost = input_data.amount - requester_user.credit.credit_back
        cost_credit_back = input_data.amount - cost
        await credit_crud.update_credit_by_user(
            db=db,
            user=requester_user,
            amount=cost,
            cash_field=CreditField.BALANCE,
            type_operation=TypeOperation.DECREASE,
        )
        await credit_crud.update_credit_by_user(
            db=db,
            user=requester_user,
            amount=cost_credit_back,
            cash_field=CreditField.CREDIT_BACK,
            type_operation=TypeOperation.DECREASE,
        )
        await credit_crud.update_credit_by_user(
            db=db,
            user=merchant_user,
            amount=merchant_profit,
            cash_field=CashField.BALANCE,
            type_operation=TypeOperation.INCREASE,
        )
        sub_main_tr = TransactionRowCreate(
            transaction_id=main_tr.id,
            status=TransactionStatusEnum.ACCEPTED,
            value=float(input_data.amount),
            text="عملیات خرید از فروشنده {}".format(merchant.contract.name),
            value_type=TransactionValueType.CREDIT,
            receiver_id=merchant.user.wallet.id,
            transferor_id=card.wallet.id,
            code=await transaction_crud.generate_code(db=db),
            reason=TransactionReasonEnum.PURCHASE,
        )
        await transaction_row_crud.create(db=db, obj_in=sub_main_tr)

        if agent.parent:
            agent_parent_profit = (agent_profit * agent.parent.profit_rate) / 100
            await credit_crud.update_credit_by_user(
                db=db,
                user=agent.parent.user,
                amount=agent_parent_profit,
                cash_field=CashField.BALANCE,
                type_operation=TypeOperation.INCREASE,
            )
            agent_parent_tr = TransactionRowCreate(
                transaction_id=main_tr.id,
                status=TransactionStatusEnum.ACCEPTED,
                value=float(agent_parent_profit),
                text="سود از فروشنده {}".format(merchant.contract.name),
                value_type=TransactionValueType.CREDIT,
                receiver_id=agent.parent.user.wallet.id,
                transferor_id=merchant.user.wallet.id,
                code=await transaction_crud.generate_code(db=db),
                reason=TransactionReasonEnum.PROFIT,
            )
            await transaction_row_crud.create(db=db, obj_in=agent_parent_tr)
            agent_profit -= agent_parent_profit
        await credit_crud.update_credit_by_user(
            db=db,
            user=agent.user,
            amount=agent_profit,
            cash_field=CashField.BALANCE,
            type_operation=TypeOperation.INCREASE,
        )
        agent_tr = TransactionRowCreate(
            transaction_id=main_tr.id,
            status=TransactionStatusEnum.ACCEPTED,
            value=float(agent_profit),
            text="سود از فروشنده {}".format(merchant.contract.name),
            value_type=TransactionValueType.CREDIT,
            receiver_id=agent.user.wallet.id,
            transferor_id=merchant.user.wallet.id,
            code=await transaction_crud.generate_code(db=db),
            reason=TransactionReasonEnum.PROFIT,
        )
        await transaction_row_crud.create(db=db, obj_in=agent_tr)

        await credit_crud.update_credit_by_user(
            db=db,
            user=icart_user,
            amount=icart_profit,
            cash_field=CashField.BALANCE,
            type_operation=TypeOperation.INCREASE,
        )
        icart_tr = TransactionRowCreate(
            transaction_id=main_tr.id,
            status=TransactionStatusEnum.ACCEPTED,
            value=float(icart_profit),
            text="سود از فروشنده {}".format(merchant.contract.name),
            value_type=TransactionValueType.CREDIT,
            receiver_id=icart_user.wallet.id,
            transferor_id=merchant.user.wallet.id,
            code=await transaction_crud.generate_code(db=db),
            reason=TransactionReasonEnum.PROFIT,
        )
        await transaction_row_crud.create(db=db, obj_in=icart_tr)
        contract_tr = TransactionRowCreate(
            transaction_id=main_tr.id,
            status=TransactionStatusEnum.ACCEPTED,
            value=float(contract_amount),
            text="برداشت سود خدمات",
            value_type=TransactionValueType.CREDIT,
            receiver_id=icart_user.wallet.id,
            transferor_id=merchant.user.wallet.id,
            code=await transaction_crud.generate_code(db=db),
            reason=TransactionReasonEnum.CONTRACT,
        )
        await transaction_row_crud.create(db=db, obj_in=contract_tr)

        # ! Credit Back
        await credit_crud.update_credit_by_user(
            db=db,
            user=requester_user,
            amount=cash_back,
            cash_field=CreditField.CREDIT_BACK,
            type_operation=TypeOperation.INCREASE,
        )
        credit_back_tr = TransactionRowCreate(
            transaction_id=main_tr.id,
            status=TransactionStatusEnum.ACCEPTED,
            value=float(cash_back),
            text="کش بک شما بابت خرید از فروشنده {}".format(merchant.contract.name),
            value_type=TransactionValueType.CREDIT,
            receiver_id=card.wallet.id,
            transferor_id=icart_user.wallet.id,
            code=await transaction_crud.generate_code(db=db),
            reason=TransactionReasonEnum.CASH_BACK,
        )
        await transaction_row_crud.create(db=db, obj_in=credit_back_tr)

    response = PurchaseOutput(
        amount=input_data.amount,
        traction_code=str(main_code),
        fee=user_fee,
        date_time=str(jdatetime.datetime.now()),
    )

    # ? Unlock user wallet
    requester_user.wallet.is_lock = False
    merchant_user.wallet.is_lock = False
    db.add(requester_user)
    db.add(merchant_user)

    await db.commit()
    return response


# ---------------------------------------------------------------------------
@router.post("/installments/purchase", response_model=InstallmentsPurchaseOutput)
async def installments_purchase(
    *,
    db: AsyncSession = Depends(deps.get_db),
    input_data: InstallmentsPurchaseInput,
) -> InstallmentsPurchaseOutput:
    """
    ! Installments Purchase request

    Parameters
    ----------
    db
        Target database connection
    input_data
        Necessary data for purchase

    Returns
    -------
    res
        result of operation

    Raises
    ------
    PosNotFoundException
    CardNotFoundException
    """
    c_time = str(jdatetime.datetime.now())
    # * Verify pos existence
    pos = await pos_crud.find_by_number(db=db, number=input_data.terminal_number)
    # * Verify merchant number
    if pos.merchant.number != input_data.merchant_number:
        raise MerchantNotFoundException()
    # * Verify Card number existence
    card = await card_crud.verify_by_number(db=db, number=input_data.card_track)
    # * Verify Card password
    verify_pass = verify_password(input_data.password, card.password)
    if not verify_pass:
        raise CardNotFoundException()

    # ! Create Installments
    amount = int(input_data.amount / input_data.number_of_installments)
    for i in range(input_data.number_of_installments):
        new_installments = InstallmentsCreate()

    # ! Pay First Section

    agent = pos.merchant.agent
    merchant = pos.merchant
    merchant_profit = (amount * (100 - 40)) / 100
    new_amount = amount - merchant_profit
    agent_profit = (new_amount * 40) / 100
    icart_profit = new_amount - agent_profit

    icart_user = await user_crud.find_by_username(
        db=db,
        username=settings.ADMIN_USERNAME,
    )

    # * Calculate Fee
    fee_response = await db.execute(
        select(Fee).order_by(Fee.limit.asc()).where(Fee.limit >= amount),
    )
    obj_list = fee_response.scalars().all()

    fee: Fee = obj_list[0]
    fee_value = (amount * fee.percentage) / 100
    if fee_value > fee.value_limit:
        fee_value = fee.value_limit

    # * Verify wallet balance
    requester_user = card.wallet.user
    merchant_user = pos.merchant.user
    if input_data.type == PosPurchaseType.DIRECT:
        # ! + Verify Fee
        if requester_user.cash.balance < amount + fee_value:
            raise LackOfMoneyException()
        # * Increase & Decrease wallet
        requester_user.cash.balance = requester_user.cash.balance - amount - fee_value
        merchant_user.cash.balance = merchant_user.cash.balance + merchant_profit
        agent.user.cash.balance = agent.user.cash.balance + agent_profit
        icart_user.cash.balance = icart_user.cash.balance + icart_profit

    else:
        if requester_user.credit.balance < amount:
            raise LackOfMoneyException()
        # ! Verify Fee
        if requester_user.cash.balance < fee_value:
            raise LackOfMoneyException()
        # * Increase & Decrease wallet
        requester_user.cash.balance = requester_user.cash.balance - fee_value
        requester_user.credit.balance = requester_user.credit.balance - amount
        merchant_user.credit.balance = merchant_user.credit.balance + merchant_profit
        agent.user.credit.balance = agent.user.credit.balance + agent_profit
        icart_user.credit.balance = icart_user.credit.balance + icart_profit

    code = randint(100000000000, 999999999999)
    user_merchant_tr = TransactionCreate(
        value=float(amount),
        text="عملیات خرید از فروشنده {}".format(merchant.contract.name),
        value_type=TransactionValueType.CASH,
        receiver_id=merchant.user.wallet.id,
        transferor_id=card.wallet.id,
        code=str(code),
        reason=TransactionReasonEnum.PURCHASE,
    )
    admin = await user_crud.find_by_username(db=db, username=settings.ADMIN_USERNAME)
    user_fee_tr = TransactionCreate(
        value=float(fee_value),
        text="کارمزد تراکنش",
        value_type=TransactionValueType.CASH,
        receiver_id=admin.wallet.id,
        transferor_id=card.wallet.id,
        code=str(randint(100000000000, 999999999999)),
        reason=TransactionReasonEnum.FEE,
    )
    admin.cash.balance += fee_value
    icart_tr = TransactionCreate(
        value=float(icart_profit),
        text="سود از فروشنده {}".format(merchant.contract.name),
        value_type=TransactionValueType.CASH,
        receiver_id=icart_user.wallet.id,
        transferor_id=merchant.user.wallet.id,
        code=str(randint(100000000000, 999999999999)),
        reason=TransactionReasonEnum.PROFIT,
    )
    agent_tr = TransactionCreate(
        value=float(agent_profit),
        text="سود از فروشنده {}".format(merchant.contract.name),
        value_type=TransactionValueType.CASH,
        receiver_id=agent.user.wallet.id,
        transferor_id=merchant.user.wallet.id,
        code=str(randint(100000000000, 999999999999)),
        reason=TransactionReasonEnum.PROFIT,
    )

    await transaction_crud.create(db=db, obj_in=user_merchant_tr)
    await transaction_crud.create(db=db, obj_in=icart_tr)
    await transaction_crud.create(db=db, obj_in=agent_tr)
    await transaction_crud.create(db=db, obj_in=user_fee_tr)
    db.add(card)
    db.add(pos)
    db.add(icart_user)
    db.add(agent)
    db.add(merchant)
    db.add(admin)
    response = PurchaseOutput(
        amount=amount,
        traction_code=str(code),
        date_time=str(jdatetime.datetime.now()),
    )

    await db.commit()
    return response
