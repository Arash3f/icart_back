from typing import Annotated, List

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.auth.exception import AccessDeniedException
from src.capital_transfer.crud import capital_transfer as capital_transfer_crud
from src.capital_transfer.exception import CapitalTransferFinishException
from src.capital_transfer.models import CapitalTransfer, CapitalTransferEnum
from src.capital_transfer.schema import (
    CapitalTransferCreate,
    CapitalTransferRead,
    CapitalTransferFilter,
    CapitalTransferFilterOrderFild,
)
from src.core.config import settings
from src.permission import permission_codes as permission
from src.schema import IDRequest, VerifyUserDep
from src.transaction.models import Transaction, TransactionValueType
from src.user.crud import user as user_crud
from src.user.models import User
from src.utils.minio_client import MinioClient
from src.wallet.crud import wallet as wallet_crud

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
async def read_capital_transfer(
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
    filter_data.receiver_id = (
        (CapitalTransfer.receiver_id == filter_data.receiver_id)
        if filter_data.receiver_id
        else True
    )

    # * Add filter fields
    query = select(CapitalTransfer).filter(
        and_(
            filter_data.gt_value,
            filter_data.lt_value,
            filter_data.transfer_type,
            filter_data.code,
            filter_data.finish,
            filter_data.receiver_id,
        ),
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
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == CapitalTransferFilterOrderFild.value:
                query = query.order_by(CapitalTransfer.value.asc())
            elif field == CapitalTransferFilterOrderFild.transfer_type:
                query = query.order_by(CapitalTransfer.transfer_type.asc())
            elif field == CapitalTransferFilterOrderFild.finish:
                query = query.order_by(CapitalTransfer.finish.asc())

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

    return capital_transfer


# ---------------------------------------------------------------------------
@router.put(path="/approve", response_model=CapitalTransferRead)
async def approve_capital_transfer(
    *,
    db: AsyncSession = Depends(deps.get_db),
    obj_data: IDRequest,
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
        Capital transfer item
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
        capital_transfer_id=obj_data.id,
    )

    if obj_current.finish:
        raise CapitalTransferFinishException()

    receiver_wallet = await wallet_crud.get(db=db, item_id=obj_current.receiver_id)
    admin_user = await user_crud.verify_existence_by_username(
        db=db,
        username=settings.ADMIN_USERNAME,
    )

    # * Update capital transfer
    obj_current.finish = True
    if obj_current.transfer_type == CapitalTransferEnum.Credit:
        tr_type = TransactionValueType.CREDIT
        receiver_wallet.credit_balance += obj_current.value
    elif obj_current.transfer_type == CapitalTransferEnum.Cash:
        tr_type = TransactionValueType.CASH
        receiver_wallet.cash_balance += obj_current.value
    # ? Create Transaction
    transaction_create = Transaction(
        value=obj_current.value,
        receiver_id=obj_current.receiver_id,
        transferor_id=admin_user.wallet.id,
        value_type=tr_type,
        text="انتقال دارایی با کد پیگیری {}".format(obj_current.code),
        capital_transfer=obj_current,
    )

    db.add(transaction_create)
    db.add(receiver_wallet)
    db.add(obj_current)
    await db.commit()
    await db.refresh(obj_current)
    return obj_current
