from typing import List,Annotated

from fastapi import (APIRouter,
                      Depends,
                      UploadFile,
                      Form,
                      File)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.capital_transfer.crud import capital_transfer as capital_transfer_crud
from src.capital_transfer.models import CapitalTransfer, CapitalTransferEnum
from src.capital_transfer.schema import (
    CapitalTransferCreate,
    CapitalTransferRead,
)
from src.transaction.crud import transaction as transaction_crud
from src.schema import IDRequest
from src.user.models import User
from src.wallet.crud import wallet as wallet_crud
from src.wallet.models import Wallet
from src.transaction.schema import TransactionCreate
from src.permission import permission_codes as permission
from src.utils.minio_client import MinioClient
from src.core.config import settings
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/capital_transfer", tags=["capital_transfer"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=CapitalTransferRead)
async def find_capital_transfer(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user(permission.VIEW_CAPITAL_TRANSFER)),
    obj_data: IDRequest,
) -> CapitalTransferRead:
    """
    ! Get one CapitalTransfer

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
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
    obj = await capital_transfer_crud.verify_existence(
        db=db,
        capital_transfer_id=obj_data.id,
    )

    return obj


# ---------------------------------------------------------------------------
@router.get(path="/list", response_model=List[CapitalTransferRead])
async def get_capital_transfer(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user(permission.VIEW_CAPITAL_TRANSFER)),
    skip: int = 0,
    limit: int = 20,
) -> List[CapitalTransferRead]:
    """
    ! Get All CapitalTransfer

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
    obj_list
        List of capital transfer

    """
    obj_list = await capital_transfer_crud.get_multi(db=db, skip=skip, limit=limit)
    return obj_list


# ---------------------------------------------------------------------------
@router.get(path="/my", response_model=List[CapitalTransferRead])
async def get_capital_transfer_list_my(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user(permission.VIEW_CAPITAL_TRANSFER)),
    skip: int = 0,
    limit: int = 20,
) -> List[CapitalTransferRead]:
    """
    ! Get All My CapitalTransfer

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
    obj_list
        List of my capital transfer

    """
    wallet = await wallet_crud.get_main_wallet_with_user_id(
        db=db,
        user_id=current_user.id,
    )
    query = select(CapitalTransfer).where(CapitalTransfer.receiver_id == wallet.id)
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
    minio:MinioClient=Depends(deps.minio_auth),
    current_user: User = Depends(deps.get_current_user(permission.CREATE_CAPITAL_TRANSFER)),
    transfer_type:Annotated[CapitalTransferEnum,Form()],
    value: Annotated[float,Form()],
    transfer_file: Annotated[UploadFile,File()],
) -> CapitalTransferRead:
    """
    ! Create CapitalTransfer with permission
    # todo: add Image

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    create_data
        Necessary data for create capital transfer

    Returns
    -------
    capital_transfer
        New position_request

    Raises
    ------
    WalletNotFoundException
        It does not happen normally
    """
    wallet = await wallet_crud.get_main_wallet_with_user_id(
        db=db,
        user_id=current_user.id,
    )
    uploaded_file = minio.client.put_object(
        object_name=transfer_file.filename,
        data=transfer_file.file,
        bucket_name=settings.MINIO_DEFAULT_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024)
    create_data = CapitalTransferCreate(
        
    )
    data = CapitalTransferCreate(file_version_id=uploaded_file.version_id,
                                 transfer_type=transfer_type,
                                 value=value,
                                 receiver_id=wallet.id,
                                 file_name=transfer_file.filename)
    capital_transfer = await capital_transfer_crud.create(db=db, obj_in=data)

    return capital_transfer


# ---------------------------------------------------------------------------
@router.put(path="/approve", response_model=CapitalTransferRead)
async def approve_capital_transfer(
    *,
    db:AsyncSession=Depends(deps.get_db),
    obj_data: IDRequest,
    current_user: User = Depends(deps.get_current_user(permission.APPROVE_CAPITAL_TRANSFER)),
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
    """
    # ? Verify capital_transfer existence
    obj_current = await capital_transfer_crud.verify_existence(
        db=db,
        capital_transfer_id=obj_data.id,
    )

    obj_current.finish = True
    receiver_wallet = await wallet_crud.get(db=db, item_id=obj_current.receiver_id)
    admin_wallet = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    admin_wallet = admin_wallet.scalar_one_or_none()
    admin_wallet.cash_balance -= obj_current.value
    
    # Todo: Create Transaction
    if obj_current.transfer_type == CapitalTransferEnum.Credit:
        receiver_wallet.credit_balance += obj_current.value
    elif obj_current.transfer_type == CapitalTransferEnum.Cash:
        receiver_wallet.cash_balance += obj_current.value

    transaction_create = TransactionCreate(value=obj_current.value,
                                           receiver_id=obj_current.receiver_id,
                                           transferor_id=admin_wallet.id,
                                           value_type=obj_current.transfer_type,
                                           value=obj_current.value,
                                           text="Capital Transfer")
    await transaction_crud.create(db=db,obj_in=transaction_create)
    db.add(receiver_wallet)
    await db.commit()
    await db.refresh(receiver_wallet)
    db.add(admin_wallet)
    await db.commit()
    await db.refresh(admin_wallet)
    db.add(obj_current)
    await db.commit()
    await db.refresh(obj_current)
    return obj_current
