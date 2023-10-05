from fastapi import APIRouter, Depends, UploadFile, File

from src import deps
from src.core.config import settings
from src.schema import ResultResponse
from src.user.models import User
from src.user.schema import UserReadWithRole
from src.utils.minio_client import MinioClient
from typing import Annotated
from src.user.crud import user as user_crud

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/user", tags=["user"])


# ---------------------------------------------------------------------------
@router.get("/me", response_model=UserReadWithRole)
async def current_user(current_user: User = Depends(deps.get_current_user())) -> User:
    """
    ! Get My data

    Parameters
    ----------
    current_user
        Requester User

    Returns
    -------
    user
        Requester User data

    """
    user = current_user
    return user


# ---------------------------------------------------------------------------
@router.post(path="/update/image", response_model=ResultResponse)
async def update_image(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    image_file: Annotated[UploadFile, File()],
    current_user: User = Depends(
        deps.get_current_user(),
    ),
) -> ResultResponse:
    """
    ! Update user image

    Parameters
    ----------
    db
    minio
    current_user
    image_file

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    """
    user = await user_crud.verify_user_existence(
        db=db,
        user_id=current_user.id,
    )

    # * Remove old image
    if user.image_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=user.image_background_name,
            version_id=user.image_background_version_id,
        )

    # * Save Contract File
    image_file = minio.client.put_object(
        data=image_file.file,
        object_name=image_file.filename,
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    user.image_version_id = image_file.version_id
    user.image_name = image_file.object_name

    db.add(user)
    await db.commit()
    return ResultResponse(result="Image Updated Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/update/background/image", response_model=ResultResponse)
async def update_background_image(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    image_file: Annotated[UploadFile, File()],
    current_user: User = Depends(
        deps.get_current_user(),
    ),
) -> ResultResponse:
    """
    ! Update user image

    Parameters
    ----------
    db
    minio
    current_user
    image_file

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    """
    user = await user_crud.verify_user_existence(
        db=db,
        user_id=current_user.id,
    )

    # * Remove old image
    if user.image_background_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=user.image_background_name,
            version_id=user.image_background_version_id,
        )

    # * Save Contract File
    image_file = minio.client.put_object(
        data=image_file.file,
        object_name=image_file.filename,
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    user.image_background_version_id = image_file.version_id
    user.image_background_name = image_file.object_name

    db.add(user)
    await db.commit()
    return ResultResponse(result="Image Updated Successfully")
