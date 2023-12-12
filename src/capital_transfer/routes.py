from typing import Annotated, List

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.auth.exception import AccessDeniedException
from src.capital_transfer.crud import capital_transfer as capital_transfer_crud
from src.capital_transfer.exception import CapitalTransferFinishException
from src.capital_transfer.models import (
    CapitalTransfer,
    CapitalTransferEnum,
    CapitalTransferStatusEnum,
)
from src.capital_transfer.schema import (
    CapitalTransferCreate,
    CapitalTransferRead,
    CapitalTransferFilter,
    CapitalTransferFilterOrderFild,
    CapitalTransferApprove,
)
from src.core.config import settings
from src.log.models import LogType
from src.permission import permission_codes as permission
from src.schema import IDRequest, VerifyUserDep
from src.user.models import User
from src.utils.minio_client import MinioClient
from src.wallet.crud import wallet as wallet_crud
from src.log.crud import log as log_crud
from src.cash.crud import cash as cash_crud, CashField, TypeOperation
from src.credit.crud import credit as credit_crud, CreditField
from src.wallet.models import Wallet

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/capital_transfer", tags=["capital_transfer"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=CapitalTransferRead)
async def find_capital_transfer(
    *,
    db=Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_CAPITAL_TRANSFER]),
    ),
    obj_data: IDRequest,
):
    """
    ! Find CapitalTransfer

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    obj_data
        Target CapitalTransfer's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    CapitalTransferNotFoundException
    """
    transfer = await capital_transfer_crud.verify_existence(
        db=db,
        capital_transfer_id=obj_data.id,
    )

    if verify_data.is_valid:
        return transfer

    # * Verify transfer receiver
    else:
        is_receiver = transfer.receiver == verify_data.user.wallet
        if is_receiver:
            return transfer
        else:
            raise AccessDeniedException()


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[CapitalTransferRead])
async def capital_transfer_list(
    *,
    db=Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_CAPITAL_TRANSFER]),
    ),
    filter_data: CapitalTransferFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[CapitalTransferRead]:
    """
    ! Get All CapitalTransfer

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
    obj_list
        List of capital transfer
    """
    # * Prepare filter fields
    filter_data.name = (
        or_(
            User.first_name.contains(filter_data.name),
        )
        if filter_data.name is not None
        else True
    )
    filter_data.last_name = (
        or_(
            User.last_name.contains(filter_data.last_name),
        )
        if filter_data.last_name is not None
        else True
    )
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code is not None
        else True
    )
    filter_data.gt_value = (
        (CapitalTransfer.value > filter_data.gt_value) if filter_data.gt_value else True
    )
    filter_data.lt_value = (
        (CapitalTransfer.value < filter_data.lt_value) if filter_data.lt_value else True
    )
    filter_data.transfer_type = (
        (CapitalTransfer.transfer_type == filter_data.transfer_type)
        if filter_data.transfer_type
        else True
    )
    filter_data.code = (
        (CapitalTransfer.code == filter_data.code) if filter_data.code else True
    )
    filter_data.finish = (
        (CapitalTransfer.finish == filter_data.finish) if filter_data.finish else True
    )
    filter_data.status = (
        (CapitalTransfer.status == filter_data.status) if filter_data.status else True
    )
    filter_data.receiver_id = (
        (CapitalTransfer.receiver_id == filter_data.receiver_id)
        if filter_data.receiver_id
        else True
    )

    # * Add filter fields
    query = (
        select(CapitalTransfer)
        .filter(
            and_(
                filter_data.name,
                filter_data.last_name,
                filter_data.gt_value,
                filter_data.lt_value,
                filter_data.transfer_type,
                filter_data.code,
                filter_data.finish,
                filter_data.receiver_id,
                filter_data.status,
            ),
        )
        .join(CapitalTransfer.receiver)
        .join(Wallet.user)
        .order_by(CapitalTransfer.created_at.desc())
    )

    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == CapitalTransferFilterOrderFild.value:
                query = query.order_by(CapitalTransfer.value.desc())
            elif field == CapitalTransferFilterOrderFild.transfer_type:
                query = query.order_by(CapitalTransfer.transfer_type.desc())
            elif field == CapitalTransferFilterOrderFild.finish:
                query = query.order_by(CapitalTransfer.finish.desc())
            elif field == CapitalTransferFilterOrderFild.created_at:
                query = query.order_by(CapitalTransfer.created_at.desc())
            elif field == CapitalTransferFilterOrderFild.updated_at:
                query = query.order_by(CapitalTransfer.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == CapitalTransferFilterOrderFild.value:
                query = query.order_by(CapitalTransfer.value.asc())
            elif field == CapitalTransferFilterOrderFild.transfer_type:
                query = query.order_by(CapitalTransfer.transfer_type.asc())
            elif field == CapitalTransferFilterOrderFild.finish:
                query = query.order_by(CapitalTransfer.finish.asc())
            elif field == CapitalTransferFilterOrderFild.created_at:
                query = query.order_by(CapitalTransfer.created_at.asc())
            elif field == CapitalTransferFilterOrderFild.updated_at:
                query = query.order_by(CapitalTransfer.updated_at.asc())

    if not verify_data.is_valid:
        query = query.where(
            CapitalTransfer.receiver == verify_data.user.wallet,
        )
    obj_list = await capital_transfer_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )

    return obj_list


# ---------------------------------------------------------------------------
@router.post(path="/create", response_model=CapitalTransferRead)
async def create_capital_transfer(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    transfer_type: Annotated[CapitalTransferEnum, Form()],
    value: Annotated[float, Form()],
    transfer_file: Annotated[UploadFile, File()],
) -> CapitalTransferRead:
    """
    ! Create CapitalTransfer with permission

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    minio
        dependency upload
    transfer_type
        Target transfer type
    value
        Target transfer value
    transfer_file
        Target file

    Returns
    -------
    capital_transfer
        New position_request
    """
    uploaded_file = minio.client.put_object(
        object_name=transfer_file.filename,
        data=transfer_file.file,
        bucket_name=settings.MINIO_CAPITAL_TRANSFER_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    code = await capital_transfer_crud.generate_code(db=db)
    create_data = CapitalTransferCreate(
        file_version_id=uploaded_file.version_id,
        transfer_type=transfer_type,
        value=value,
        receiver_id=current_user.wallet.id,
        file_name=transfer_file.filename,
        code=code,
    )
    capital_transfer = await capital_transfer_crud.create(db=db, obj_in=create_data)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.UPDATE_AGENT,
        user_id=current_user.id,
        detail="درخواست اعتبار با شناسه {} با موفقیت توسط کاربر {} ایجاد شد".format(
            capital_transfer.code,
            current_user.username,
        ),
    )

    return capital_transfer


# ---------------------------------------------------------------------------
@router.put(path="/approve", response_model=CapitalTransferRead)
async def approve_capital_transfer(
    *,
    db: AsyncSession = Depends(deps.get_db),
    obj_data: CapitalTransferApprove,
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.APPROVE_CAPITAL_TRANSFER]),
    ),
) -> CapitalTransferRead:
    """
    ! Approve CapitalTransfer

    Parameters
    ----------
    db
        Target database connection
    obj_data
        Capital transfer id and approve value
    current_user
        Requester User

    Returns
    -------
    obj_current
        Updated capital transfer

    Raises
    ------
    CapitalTransferNotFoundException
    CapitalTransferFinishException
    """
    # ? Verify capital_transfer existence
    obj_current = await capital_transfer_crud.verify_existence(
        db=db,
        capital_transfer_id=obj_data.where.id,
    )

    if obj_current.finish:
        raise CapitalTransferFinishException()

    # ! Reject
    if not obj_data.approve:
        obj_current.finish = True
        obj_current.status = CapitalTransferStatusEnum.FAILED

    else:
        user_wallet: Wallet = await wallet_crud.get(
            db=db,
            item_id=obj_current.receiver_id,
        )

        # * Update capital transfer
        obj_current.finish = True
        if obj_current.transfer_type == CapitalTransferEnum.Credit:
            await credit_crud.update_credit_by_user(
                db=db,
                credit_field=CreditField.BALANCE,
                type_operation=TypeOperation.INCREASE,
                user=user_wallet.user,
                amount=obj_current.value,
            )
        elif obj_current.transfer_type == CapitalTransferEnum.Cash:
            await cash_crud.update_cash_by_user(
                db=db,
                cash_field=CashField.BALANCE,
                type_operation=TypeOperation.INCREASE,
                user=user_wallet.user,
                amount=obj_current.value,
            )

    db.add(obj_current)
    await db.commit()
    await db.refresh(obj_current)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.APPROVE_CAPITAL_TRANSFER,
        user_id=current_user.id,
        detail="درخواست اعتبار با شناسه {} با موفقیت توسط ادمین {} تایید شد".format(
            obj_current.code,
            current_user.username,
        ),
    )

    return obj_current
