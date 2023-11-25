import requests
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.card.crud import CardValueType
from src.core.config import settings
from src.exception import InCorrectDataException
from src.log.crud import log as log_crud
from src.transaction.models import (
    TransactionStatusEnum,
    TransactionValueType,
    TransactionReasonEnum,
)
from src.permission import permission_codes as permission
from src.transaction.schema import TransactionCreate, TransactionRowCreate
from src.zibal.schema import (
    ZibalVerifyInput,
    NationalIdentityInquiryInput,
    NationalIdentityInquiryOutput,
)
from src.log.models import LogType
from src.transaction.crud import transaction as transaction_crud
from src.user.crud import user as user_crud
from src.card.crud import card as card_crud
from src.cash.crud import cash as cash_crud, CashField, TypeOperation
from src.transaction.crud import transaction_row as transaction_row_crud
from src.schema import ResultResponse
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/zibal", tags=["zibal"])


# ---------------------------------------------------------------------------
@router.post("/cash/charging/verify/", response_model=ResultResponse)
async def cash_charging_verify(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    verify_data: ZibalVerifyInput,
) -> ResultResponse:
    """
    ! Create a Transaction for zibal IPG

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    verify_data
        Necessary data for create zibal ipg

    Returns
    -------
    response
        Result of operation
    """
    url = "https://gateway.zibal.ir/v1/verify"
    res = requests.post(
        headers={
            "Content-Type": "application/json",
        },
        url=url,
        json={
            "merchant": "6559b8aea9a498000fde7cc8",
            "trackId": int(verify_data.track_id),
        },
    )

    response = res.json()

    if response["result"] == 100 and response["message"] == "success":
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
            status=TransactionStatusEnum.ACCEPTED,
            value=float(response["amount"]),
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
            status=TransactionStatusEnum.ACCEPTED,
            value=float(response["amount"]),
            text="عملیات شارژ کردن کیف پول کاربر",
            value_type=TransactionValueType.CASH,
            receiver_id=receiver_card.id,
            transferor_id=transferor_card.id,
            code=main_code,
            zibal_track_id=str(response["trackId"]),
            reason=TransactionReasonEnum.WALLET_CHARGING,
        )
        await transaction_row_crud.create(db=db, obj_in=merchant_fee_tr)

        await cash_crud.update_cash_by_user(
            db=db,
            user=current_user,
            amount=response["amount"],
            cash_field=CashField.BALANCE,
            type_operation=TypeOperation.INCREASE,
        )

        # ? Generate Log
        await log_crud.auto_generate(
            db=db,
            user_id=current_user.id,
            log_type=LogType.CHARGING_CARD,
            detail="حساب کاربر {} با موفقیت به اندازه {} شارژ شد".format(
                current_user.id,
                str(response["amount"]),
            ),
        )

        await db.commit()
    return ResultResponse(result="Transaction Check")


# ---------------------------------------------------------------------------
@router.post("/national/identity/verify/", response_model=NationalIdentityInquiryOutput)
async def national_identity_verify(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_USER_REQUEST]),
    ),
    verify_data: NationalIdentityInquiryInput,
) -> NationalIdentityInquiryOutput:
    auth_token = "Bearer d3309a731ef64381be20a6a564ede39c"

    res = requests.post(
        url="https://api.zibal.ir/v1/facility/nationalIdentityInquiry/",
        headers={
            "Authorization": auth_token,
        },
        json={
            "nationalCode": verify_data.national_code,
            "birthDate": verify_data.birth_date,
        },
    )

    res = res.json()

    if res["data"]:
        if res["data"]["matched"]:
            return NationalIdentityInquiryOutput(
                matched=res["data"]["matched"].matched,
                lastName=res["data"]["matched"].lastName,
                fatherName=res["data"]["matched"].fatherName,
                firstName=res["data"]["matched"].firstName,
                nationalCode=res["data"]["matched"].nationalCode,
                isDead=res["data"]["matched"].isDead,
                alive=res["data"]["matched"].alive,
            )

    raise InCorrectDataException()
