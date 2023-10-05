import io

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from src import deps
from src.capital_transfer.crud import capital_transfer as capital_transfer_crud
from src.contract.crud import contract as contract_crud
from src.user.crud import user as user_crud
from src.core.config import settings
from src.schema import IDRequest
from src.utils.minio_client import MinioClient

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/media", tags=["media"])


@router.post(path="/capital_transfer/find")
async def get_capital_transfer_media(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    capital_transfer: IDRequest,
):
    """
    ! Find Capital Transfer Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    capital_transfer
        Target capital transfer id

    Returns
    -------
    res
        found File

    Raises
    ------
    CapitalTransferNotFoundException
    """
    obj = await capital_transfer_crud.verify_existence(
        db=db,
        capital_transfer_id=capital_transfer.id,
    )

    media_file = minio.client.get_object(
        bucket_name=settings.MINIO_CAPITAL_TRANSFER_BUCKET,
        object_name=obj.file_name,
        version_id=obj.file_version_id,
    )
    return StreamingResponse(io.BytesIO(media_file.read()), media_type="image/png")


@router.post(path="/contract/find")
async def get_contract_media(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    contract: IDRequest,
):
    """
    ! Find Contract Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    contract
        Target contract id

    Returns
    -------
    res
        found File

    Raises
    ------
    CapitalTransferNotFoundException
    """
    obj = await contract_crud.verify_existence(
        db=db,
        contract_id=contract.id,
    )

    media_file = minio.client.get_object(
        bucket_name=settings.MINIO_CONTRACT_BUCKET,
        object_name=obj.file_name,
        version_id=obj.file_version_id,
    )
    return StreamingResponse(io.BytesIO(media_file.read()), media_type="image/png")


@router.post(path="/user/background/find")
async def get_background_file(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    user: IDRequest,
):
    """
    ! Find Contract Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    contract
        Target contract id

    Returns
    -------
    res
        found File

    Raises
    ------
    UserNotFoundException
    """
    obj = await user_crud.verify_existence(
        db=db,
        user_id=user.id,
    )

    background_file = minio.client.get_object(
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        object_name=obj.file_name,
        version_id=obj.file_version_id,
    )
    return StreamingResponse(io.BytesIO(background_file.read()), media_type="image/png")


@router.post(path="/user/image/find")
async def get_image_file(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    user: IDRequest,
):
    """
    ! Find User Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    user
        Target user id

    Returns
    -------
    res
        found File

    Raises
    ------
    UserNotFoundException
    """
    obj = await user_crud.verify_existence(
        db=db,
        user_id=user.id,
    )

    image_file = minio.client.get_object(
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        object_name=obj.file_name,
        version_id=obj.file_version_id,
    )
    return StreamingResponse(io.BytesIO(image_file.read()), media_type="image/png")
