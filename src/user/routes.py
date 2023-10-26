from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import select, and_

from src import deps
from src.core.config import settings
from src.schema import ResultResponse
from src.user.models import User
from src.user.schema import UserMeResponse, UserRead, UserFilter, UpdateUserRequest
from src.utils.minio_client import MinioClient
from typing import Annotated, List
from src.user.crud import user as user_crud
from src.location.crud import location as location_crud
from src.permission import permission_codes as permission

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/user", tags=["user"])


# ---------------------------------------------------------------------------
@router.get("/me", response_model=UserMeResponse)
async def current_user(
    current_user: User = Depends(deps.get_current_user()),
) -> UserMeResponse:
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
    """
    # * Remove old image
    if current_user.image_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=current_user.image_name,
            version_id=current_user.image_version_id,
        )

    # * Save Contract File
    image_file = minio.client.put_object(
        data=image_file.file,
        object_name=image_file.filename,
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    current_user.image_version_id = image_file.version_id
    current_user.image_name = image_file.object_name

    db.add(current_user)
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
    """
    # * Remove old image
    if current_user.image_background_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=current_user.image_background_name,
            version_id=current_user.image_background_version_id,
        )

    # * Save Contract File
    image_file = minio.client.put_object(
        data=image_file.file,
        object_name=image_file.filename,
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    current_user.image_background_version_id = image_file.version_id
    current_user.image_background_name = image_file.object_name

    db.add(current_user)
    await db.commit()
    return ResultResponse(result="Image Updated Successfully")


@router.delete(path="/image/delete", response_model=ResultResponse)
async def delete_image_file(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    current_user: User = Depends(deps.get_current_user()),
) -> ResultResponse:
    """
    ! Delete User Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    current_user
        Requester User

    Returns
    -------
    res
        result of operation
    """
    if current_user.image_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=current_user.image_name,
            version_id=current_user.image_version_id,
        )
        current_user.image_name = None
        current_user.image_version_id = None
        db.add(current_user)
        await db.commit()

    return ResultResponse(result="Image Deleted Successfully")


@router.delete(path="/background/delete", response_model=ResultResponse)
async def get_background_file(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    current_user: User = Depends(deps.get_current_user()),
) -> ResultResponse:
    """
    ! Delete User Background Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    current_user
        Requester User

    Returns
    -------
    res
        result of operation
    """
    if current_user.image_background_version_id:
        minio.client.get_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=current_user.image_background_name,
            version_id=current_user.image_background_version_id,
        )
        current_user.image_background_name = None
        current_user.image_background_version_id = None
        db.add(current_user)
        await db.commit()

    return ResultResponse(result="Image Deleted Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[UserRead])
async def user_list(
    *,
    db=Depends(deps.get_db),
    filter_data: UserFilter,
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[UserRead]:
    """
    ! Get All User

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    filter_data
        Filter data
    skip
        Pagination skip
    limit
        Pagination limit

    Returns
    -------
    obj_list
        List of user
    """
    # * Prepare filter fields
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code
        else True
    )
    filter_data.phone_number = (
        (User.phone_number.contains(filter_data.phone_number))
        if filter_data.phone_number
        else True
    )

    # * Add filter fields
    query = select(User).filter(
        and_(
            filter_data.phone_number,
            filter_data.national_code,
        ),
    )
    # * Find All agent with filters
    obj_list = await user_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list


# ---------------------------------------------------------------------------
@router.put(path="/update", response_model=UserRead)
async def update_user(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_USER]),
    ),
    update_data: UpdateUserRequest,
) -> UserRead:
    """
    ! Update User

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update user

    Returns
    -------
    obj
        Updated user

    Raises
    ------
    LocationNotFoundException
    UserNotFoundException
    """
    # * Verify user existence
    obj_current = await user_crud.verify_existence(
        db=db,
        user_id=update_data.where.id,
    )

    # * Verify location existence
    if update_data.data.location_id:
        await location_crud.verify_existence(
            db=db,
            location_id=update_data.data.parent_id,
        )

    obj = await location_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )
    return obj
