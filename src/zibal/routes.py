import requests
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.card.crud import CardValueType
from src.core.config import settings
from src.exception import TechnicalProblemException
from src.log.crud import log as log_crud
from src.transaction.models import (
    TransactionStatusEnum,
    TransactionValueType,
    TransactionReasonEnum,
)
from src.transaction.schema import TransactionCreate, TransactionRowCreate
from src.zibal.schema import ZibalCashChargingRequest, ZibalCashChargingRequestResponse
from src.log.models import LogType
from src.transaction.crud import transaction as transaction_crud
from src.user.crud import user as user_crud
from src.card.crud import card as card_crud
from src.wallet.crud import wallet as wallet_crud
from src.cash.crud import cash as cash_crud, CashField, TypeOperation
from src.transaction.crud import transaction_row as transaction_row_crud
from src.schema import ResultResponse
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/zibal", tags=["zibal"])


# ---------------------------------------------------------------------------
@router.post("/cash/charging/request", response_model=ZibalCashChargingRequestResponse)
async def delete_zibal(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    ipg_data: ZibalCashChargingRequest,
) -> ZibalCashChargingRequestResponse:
    """
    ! Create a Transaction for zibal IPG

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    ipg_data
        Necessary data for create zibal ipg

    Returns
    -------
    response
        Result of operation
    """
    url = "https://gateway.zibal.ir/v1/request"
    res = requests.post(
        headers={
            "Content-Type": "application/json",
        },
        url=url,
        json={
            "merchant": "6559b8aea9a498000fde7cc8",
            "amount": int(ipg_data.amount),
            "callbackUrl": "https://icarts.ir/zibal/cash/charging/verify/",
            "description": "عملیات شارژ کردن کیف پول کاربر با شناسه {}".format(
                current_user.id,
            ),
        },
    )

    response = res.json()
    if response["message"] != "success":
        raise TechnicalProblemException()

    admin_user = await user_crud.verify_existence_by_username(
        db=db,
        username=settings.ADMIN_USERNAME,
    )

    transferor_card = await card_crud.get_active_card(
        db=db,
        card_value_type=CardValueType.CASH,
        wallet=admin_user.wallet,
    )
    receiver_card = await card_crud.get_active_card(
        db=db,
        card_value_type=CardValueType.CASH,
        wallet=current_user.wallet,
    )

    # ! Main
    main_code = await transaction_crud.generate_code(db=db)
    main_tr = TransactionCreate(
        status=TransactionStatusEnum.IN_PROGRESS,
        value=float(ipg_data.amount),
        text="عملیات شارژ کردن کیف پول کاربر",
        value_type=TransactionValueType.CASH,
        receiver_id=receiver_card.id,
        transferor_id=transferor_card.id,
        code=main_code,
        reason=TransactionReasonEnum.WALLET_CHARGING,
    )
    main_tr = await transaction_crud.create(db=db, obj_in=main_tr)
    merchant_fee_tr = TransactionRowCreate(
        transaction_id=main_tr.id,
        status=TransactionStatusEnum.IN_PROGRESS,
        value=float(ipg_data.amount),
        text="عملیات شارژ کردن کیف پول کاربر",
        value_type=TransactionValueType.CASH,
        receiver_id=receiver_card.id,
        transferor_id=transferor_card.id,
        code=main_code,
        zibal_track_id=str(response["trackId"]),
        reason=TransactionReasonEnum.WALLET_CHARGING,
    )
    await transaction_row_crud.create(db=db, obj_in=merchant_fee_tr)

    return ZibalCashChargingRequestResponse(track_id=str(response["trackId"]))


# ---------------------------------------------------------------------------
@router.get(
    "/cash/charging/verify/{trackId}/{success}/{status}/",
    response_model=ResultResponse,
)
async def create_zibal(
    *,
    db: AsyncSession = Depends(deps.get_db),
    trackId: int,
    success: int,
    status: int,
) -> ResultResponse:
    """
    ! Verify Zibal Request

    Parameters
    ----------
    db
        Target database connection
    trackId
        zibal track id
    success
        operation success value
    status
        operation status

    Returns
    -------
    zibal
        verify

    Raises
    ------
    TransactionNotFoundException
    """
    # todo: just from Zibal
    transaction_row = await transaction_row_crud.verify_by_zibal_track_id(
        db=db,
        zibal_track_id=trackId,
    )
    if (
        status == 2
        and success == 1
        and transaction_row.status == TransactionStatusEnum.IN_PROGRESS
    ):
        wallet = await wallet_crud.verify_existence(
            db=db,
            wallet_id=transaction_row.receiver_id,
        )
        await cash_crud.update_cash_by_user(
            db=db,
            user=wallet.user,
            amount=transaction_row.value,
            cash_field=CashField.BALANCE,
            type_operation=TypeOperation.INCREASE,
        )
        transaction_row.status == TransactionStatusEnum.ACCEPTED

        transaction = await transaction_crud.verify_existence(
            db=db,
            transaction_id=transaction_row.transaction_id,
        )
        transaction.status = TransactionStatusEnum.ACCEPTED

        db.add(transaction_row)
        db.add(transaction)
        await db.commit()

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=wallet.user_id,
        log_type=LogType.CHARGING_CARD,
        detail="حساب کاربر {} با موفقیت به اندازه {} شارژ شد".format(
            wallet.user_id,
            transaction_row.value,
        ),
    )

    return ResultResponse(result="Successfully")
