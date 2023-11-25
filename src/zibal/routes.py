import requests
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.deposit.schemas import DepositCreate, DepositApprove
from src.exception import InCorrectDataException
from src.log.crud import log as log_crud
from src.deposit.crud import deposit as deposit_crud
from src.permission import permission_codes as permission
from src.zibal.schema import (
    NationalIdentityInquiryInput,
    NationalIdentityInquiryOutput,
)
from src.log.models import LogType
from src.cash.crud import cash as cash_crud, CashField, TypeOperation
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
    verify_data: DepositApprove,
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

    if response["result"] == 201:
        return ResultResponse(result=response["message"])

    if response["result"] == 100 and response["message"] == "success":
        create_data = DepositCreate(
            amount=response["amount"],
            zibal_track_id=verify_data.track_id,
            wallet_id=current_user.wallet.id,
        )

        await deposit_crud.create(db=db, obj_in=create_data)

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

    if res["result"] == 1:
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
