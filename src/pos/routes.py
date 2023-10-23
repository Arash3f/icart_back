from datetime import datetime
from random import randint

from fastapi import APIRouter, Depends
from pytz import timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import jdatetime
from src import deps
from src.auth.exception import (
    IncorrectUsernameOrPasswordException,
    InactiveUserException,
)
from src.card.exception import CardNotFoundException
from src.core.config import settings
from src.core.security import verify_password
from src.fee.models import Fee
from src.installments.schema import InstallmentsCreate
from src.merchant.crud import merchant as merchant_crud
from src.card.crud import card as card_crud
from src.merchant.exception import MerchantNotFoundException
from src.permission import permission_codes as permission
from src.pos.crud import pos as pos_crud
from src.transaction.models import TransactionValueType, TransactionReasonEnum
from src.transaction.schema import TransactionCreate
from src.user.crud import user as user_crud
from src.auth.crud import auth as auth_crud
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
    ConfigPosOutput,
    PosPurchaseType,
    ConfigurationPosInput,
    ConfigurationPosOutput,
    InstallmentsPurchaseOutput,
    InstallmentsPurchaseInput,
)
from src.schema import DeleteResponse, IDRequest, ResultResponse
from src.user.models import User
from src.wallet.exception import LackOfMoneyException

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
    await pos_crud.verify_existence(db=db, pos_id=delete_data.id)
    # * Delete Pos
    await pos_crud.delete(db=db, item_id=delete_data.id)

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
    filter_data.merchant_id = (
        (Pos.merchant_id == filter_data.merchant_id)
        if filter_data.merchant_id
        else True
    )
    # * Add filter fields
    query = select(Pos).filter(
        filter_data.merchant_id,
    )
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
        raise PosNotFoundException()

    return ConfigurationPosOutput(
        terminal_number=pos.number,
        merchant_number=pos.merchant.number,
        tel=pos.merchant.user.phone_number,
        date_time=str(jdatetime.datetime.now()),
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
        terminal_number=pos.number,
        merchant_number=pos.merchant.number,
        tel=pos.merchant.user.phone_number,
        date_time=str(jdatetime.datetime.now()),
    )


# ---------------------------------------------------------------------------
@router.post("/balance", response_model=BalanceOutput)
async def config(
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
    # * Verify pos existence
    pos = await pos_crud.find_by_number(db=db, number=card_data.terminal_number)

    if pos.merchant.number != card_data.merchant_number:
        raise PosNotFoundException()

    # * Verify Card number existence
    card = await card_crud.verify_by_number(db=db, number=card_data.card_track)

    # * Verify Card password
    verify_pass = verify_password(card_data.password, card.password)
    if not verify_pass:
        return None

    response = BalanceOutput(
        amount=card.wallet.user.cash.balance,
        terminal_number=pos.number,
        merchant_number=pos.merchant.number,
        code=randint(100000, 999999),
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
        raise MerchantNotFoundException(time=c_time)
    # * Verify Card number existence
    card = await card_crud.verify_by_number(db=db, number=input_data.card_track)
    # * Verify Card password
    verify_pass = verify_password(input_data.password, card.password)
    if not verify_pass:
        raise CardNotFoundException(time=c_time)

    agent = pos.merchant.agent
    merchant = pos.merchant
    merchant_profit = (input_data.amount * (100 - 40)) / 100
    new_amount = input_data.amount - merchant_profit
    agent_profit = (new_amount * 40) / 100
    icart_profit = new_amount - agent_profit

    icart_user = await user_crud.find_by_username(
        db=db,
        username=settings.ADMIN_USERNAME,
    )

    # * Calculate Fee
    fee_response = await db.execute(
        select(Fee).order_by(Fee.limit.asc()).where(Fee.limit >= input_data.amount),
    )
    obj_list = fee_response.scalars().all()

    fee: Fee = obj_list[0]
    fee_value = (input_data.amount * fee.percentage) / 100
    if fee_value > fee.value_limit:
        fee_value = fee.value_limit

    # * Verify wallet balance
    requester_user = card.wallet.user
    merchant_user = pos.merchant.user
    if input_data.type == PosPurchaseType.DIRECT:
        # ! + Verify Fee
        if requester_user.cash.balance < input_data.amount + fee_value:
            raise LackOfMoneyException()
        # * Increase & Decrease wallet
        requester_user.cash.balance = (
            requester_user.cash.balance - input_data.amount - fee_value
        )
        merchant_user.cash.balance = merchant_user.cash.balance + merchant_profit
        agent.user.cash.balance = agent.user.cash.balance + agent_profit
        icart_user.cash.balance = icart_user.cash.balance + icart_profit

    else:
        if requester_user.credit.balance < input_data.amount:
            raise LackOfMoneyException()
        # ! Verify Fee
        if requester_user.cash.balance < fee_value:
            raise LackOfMoneyException()
        # * Increase & Decrease wallet
        requester_user.cash.balance = requester_user.cash.balance - fee_value
        requester_user.credit.balance = (
            requester_user.credit.balance - input_data.amount
        )
        merchant_user.credit.balance = merchant_user.credit.balance + merchant_profit
        agent.user.credit.balance = agent.user.credit.balance + agent_profit
        icart_user.credit.balance = icart_user.credit.balance + icart_profit

    code = randint(100000000000, 999999999999)
    user_merchant_tr = TransactionCreate(
        value=float(input_data.amount),
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
        amount=input_data.amount,
        traction_code=str(code),
        date_time=str(jdatetime.datetime.now()),
    )

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
        raise MerchantNotFoundException(time=c_time)
    # * Verify Card number existence
    card = await card_crud.verify_by_number(db=db, number=input_data.card_track)
    # * Verify Card password
    verify_pass = verify_password(input_data.password, card.password)
    if not verify_pass:
        raise CardNotFoundException(time=c_time)

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
