import io

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from src import deps
from src.capital_transfer.crud import capital_transfer as capital_transfer_crud
from src.contract.crud import contract as contract_crud
from src.media.schema import UserId
from src.user.crud import user as user_crud
from src.user_request.crud import user_request as user_request_crud
from src.core.config import settings
from src.schema import IDRequest, ResultResponse
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

    if obj.file_version_id:
        media_file = minio.client.get_object(
            bucket_name=settings.MINIO_CAPITAL_TRANSFER_BUCKET,
            object_name=obj.file_name,
            version_id=obj.file_version_id,
        )
        return StreamingResponse(io.BytesIO(media_file.read()), media_type="image/png")

    else:
        return ResultResponse(result="Image Not Found")


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

    if obj.file_version_id:
        media_file = minio.client.get_object(
            bucket_name=settings.MINIO_CONTRACT_BUCKET,
            object_name=obj.file_name,
            version_id=obj.file_version_id,
        )
        return StreamingResponse(io.BytesIO(media_file.read()), media_type="image/png")

    else:
        return ResultResponse(result="Image Not Found")


@router.post(path="/user/background/find")
async def get_background_file(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    user: IDRequest,
):
    """
    ! Find User Background Image

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

    if obj.image_background_version_id:
        background_file = minio.client.get_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=obj.image_background_name,
            version_id=obj.image_background_version_id,
        )
        return StreamingResponse(
            io.BytesIO(background_file.read()),
            media_type="image/png",
        )

    else:
        return ResultResponse(result="Image Not Found")


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

    if obj.image_version_id:
        image_file = minio.client.get_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=obj.image_name,
            version_id=obj.image_version_id,
        )
        return StreamingResponse(io.BytesIO(image_file.read()), media_type="image/png")
    else:
        return ResultResponse(result="Image Not Found")


@router.post(path="/user_request/national_card_front/find")
async def get_national_card_front_file(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    where_data: UserId,
):
    """
    ! Find User Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    where_data
        Target user id

    Returns
    -------
    res
        found File

    Raises
    ------
    UserNotFoundException
    """
    obj = await user_request_crud.verify_existence_by_user_id(
        db=db,
        user_id=where_data.user_id,
    )

    if obj.national_card_front_version_id:
        national_card_front_file = minio.client.get_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=obj.national_card_front_name,
            version_id=obj.national_card_front_version_id,
        )
        return StreamingResponse(
            io.BytesIO(national_card_front_file.read()),
            media_type="image/png",
        )
    else:
        return ResultResponse(result="Image Not Found")


@router.post(path="/user_request/national_card_back/find")
async def get_national_card_back_file(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    where_data: UserId,
):
    """
    ! Find User Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    where_data
        Target user id

    Returns
    -------
    res
        found File

    Raises
    ------
    UserNotFoundException
    """
    obj = await user_request_crud.verify_existence_by_user_id(
        db=db,
        user_id=where_data.user_id,
    )

    if obj.national_card_back_version_id:
        national_card_back_file = minio.client.get_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=obj.national_card_back_name,
            version_id=obj.national_card_back_version_id,
        )
        return StreamingResponse(
            io.BytesIO(national_card_back_file.read()),
            media_type="image/png",
        )
    else:
        return ResultResponse(result="Image Not Found")


@router.post(path="/user_request/birth_certificate/find")
async def get_birth_certificate_file(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    where_data: UserId,
):
    """
    ! Find User Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    where_data
        Target user id

    Returns
    -------
    res
        found File

    Raises
    ------
    UserNotFoundException
    """
    obj = await user_request_crud.verify_existence_by_user_id(
        db=db,
        user_id=where_data.user_id,
    )

    if obj.birth_certificate_version_id:
        birth_certificate_file = minio.client.get_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=obj.birth_certificate_name,
            version_id=obj.birth_certificate_version_id,
        )
        return StreamingResponse(
            io.BytesIO(birth_certificate_file.read()),
            media_type="image/png",
        )
    else:
        return ResultResponse(result="Image Not Found")


@router.post(path="/user_request/video/find")
async def get_video_file(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    where_data: UserId,
):
    """
    ! Find User video

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    where_data
        Target user id

    Returns
    -------
    res
        found File

    Raises
    ------
    UserNotFoundException
    """
    obj = await user_request_crud.verify_existence_by_user_id(
        db=db,
        user_id=where_data.user_id,
    )

    if obj.video_version_id:
        video_file = minio.client.get_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=obj.video_name,
            version_id=obj.video_version_id,
        )
        # todo: not work
        return StreamingResponse(
            io.BytesIO(video_file.stream()),
            media_type="video/mp4",
        )
    else:
        return ResultResponse(result="Image Not Found")
