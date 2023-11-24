from typing import List, Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import select, and_

from src import deps
from src.core.config import settings
from src.user_request.crud import user_request as user_request_crud
from src.location.crud import location as location_crud
from src.user.crud import user as user_crud
from src.user_request.models import UserRequest
from src.user_request.schema import (
    UserRequestRead,
    UserRequestFilter,
    ApproveUserRequest,
    UpdateUserRequest,
    CreateUserRequest,
)
from src.permission import permission_codes as permission
from src.schema import IDRequest, ResultResponse
from src.user.models import User
from src.utils.minio_client import MinioClient

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/user_request", tags=["user_request"])


# ---------------------------------------------------------------------------
@router.put(path="/approve", response_model=UserRequestRead)
async def update_user_request(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.APPROVE_USER_REQUEST]),
    ),
    obj_data: ApproveUserRequest,
) -> UserRequestRead:
    """
    ! Approve UserRequest

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Necessary data for approve user_request

    Returns
    -------
    obj
        New user_request

    Raises
    ------
    LocationNotFoundException
    """
    # * Check user
    await user_crud.verify_existence(db=db, user_id=obj_data.data.user_id)

    if obj_data.data.location_id:
        # * Check location ?
        await location_crud.verify_existence(
            db=db,
            location_id=obj_data.data.location_id,
        )

    obj_in = UpdateUserRequest(
        **obj_data.data.model_dump(),
    )
    obj = await user_request_crud.update(
        db=db,
        obj_new=obj_in,
        obj_current=current_user.user_request,
    )

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=UserRequestRead)
async def find_user_request(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_USER_REQUEST]),
    ),
    obj_data: IDRequest,
) -> UserRequestRead:
    """
    ! Find UserRequest

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target UserRequest's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    UserRequestNotFoundException
    """
    # * Verify user_request existence
    obj = await user_request_crud.verify_existence(db=db, user_request_id=obj_data.id)

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/me", response_model=UserRequestRead)
async def me_user_request(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user(),
    ),
) -> UserRequestRead:
    """
    ! My UserRequest

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    UserRequestNotFoundException
    """
    find_user_request = await user_request_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    print(find_user_request)

    if find_user_request:
        return find_user_request

    user_request = CreateUserRequest(
        user_id=current_user.id,
    )
    user_request = await user_request_crud.create(
        db=db,
        obj_in=user_request,
    )
    return user_request


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[UserRequestRead])
async def user_request_list(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_USER_REQUEST]),
    ),
    filter_data: UserRequestFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[UserRequestRead]:
    """
    ! Get All UserRequest

    Parameters
    ----------
    db
        Target database connection
    skip
        Pagination skip
    limit
        Pagination limit
    filter_data
        Filter data

    Returns
    -------
    obj_list
        List of ability
    """
    # * Prepare filter fields
    filter_data.status = (
        (UserRequest.status == filter_data.status) if filter_data.status else True
    )
    filter_data.location_id = (
        (UserRequest.location_id == filter_data.location_id)
        if filter_data.location_id
        else True
    )
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code
        else True
    )

    # * Add filter fields
    query = (
        select(UserRequest)
        .filter(
            and_(
                filter_data.status,
                filter_data.location_id,
                filter_data.national_code,
            ),
        )
        .join(UserRequest.user)
        .order_by(UserRequest.created_at.desc())
    )

    # * Find All agent with filters
    obj_list = await user_request_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )

    return obj_list


# ---------------------------------------------------------------------------
@router.post(path="/update/national_card_front", response_model=ResultResponse)
async def update_national_card_front(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    image_file: Annotated[UploadFile, File()],
    current_user: User = Depends(
        deps.get_current_user(),
    ),
) -> ResultResponse:
    """
    ! Update user national_card_front

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
    user_request = await user_request_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    if not user_request:
        user_request = UserRequest()

    # * Remove old image
    if user_request.national_card_front_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=user_request.national_card_front_name,
            version_id=user_request.national_card_front_version_id,
        )

    # * Save Contract File
    national_card_front_file = minio.client.put_object(
        data=image_file.file,
        object_name=image_file.filename,
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    user_request.national_card_front_version_id = national_card_front_file.version_id
    user_request.national_card_front_name = national_card_front_file.object_name
    user_request.user_id = current_user.id

    db.add(user_request)
    await db.commit()
    return ResultResponse(result="Image Updated Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/update/national_card_back", response_model=ResultResponse)
async def update_national_card_back(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    image_file: Annotated[UploadFile, File()],
    current_user: User = Depends(
        deps.get_current_user(),
    ),
) -> ResultResponse:
    """
    ! Update user national_card_back

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
    user_request = await user_request_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    if not user_request:
        user_request = UserRequest()

    # * Remove old image
    if user_request.national_card_back_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=user_request.national_card_back_name,
            version_id=user_request.national_card_back_version_id,
        )

    # * Save Contract File
    national_card_back_file = minio.client.put_object(
        data=image_file.file,
        object_name=image_file.filename,
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    user_request.national_card_back_version_id = national_card_back_file.version_id
    user_request.national_card_back_name = national_card_back_file.object_name
    user_request.user_id = current_user.id

    db.add(user_request)
    await db.commit()
    return ResultResponse(result="Image Updated Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/update/birth_certificate", response_model=ResultResponse)
async def update_birth_certificate(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    image_file: Annotated[UploadFile, File()],
    current_user: User = Depends(
        deps.get_current_user(),
    ),
) -> ResultResponse:
    """
    ! Update user birth_certificate

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
    user_request = await user_request_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    if not user_request:
        user_request = UserRequest()

    # * Remove old image
    if user_request.birth_certificate_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=user_request.birth_certificate_name,
            version_id=user_request.birth_certificate_version_id,
        )

    # * Save Contract File
    birth_certificate_file = minio.client.put_object(
        data=image_file.file,
        object_name=image_file.filename,
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    user_request.birth_certificate_version_id = birth_certificate_file.version_id
    user_request.birth_certificate_name = birth_certificate_file.object_name
    user_request.user_id = current_user.id

    db.add(user_request)
    await db.commit()
    return ResultResponse(result="Image Updated Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/update/video", response_model=ResultResponse)
async def update_video(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    image_file: Annotated[UploadFile, File()],
    current_user: User = Depends(
        deps.get_current_user(),
    ),
) -> ResultResponse:
    """
    ! Update user video

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
    user_request = await user_request_crud.find_by_user_id(
        db=db,
        user_id=current_user.id,
    )

    if not user_request:
        user_request = UserRequest()

    # * Remove old image
    if user_request.video_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
            object_name=user_request.video_name,
            version_id=user_request.video_version_id,
        )

    # * Save Contract File
    video_file = minio.client.put_object(
        data=image_file.file,
        object_name=image_file.filename,
        bucket_name=settings.MINIO_PROFILE_IMAGE_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    user_request.video_version_id = video_file.version_id
    user_request.video_name = video_file.object_name
    user_request.user_id = current_user.id

    db.add(user_request)
    await db.commit()
    return ResultResponse(result="video Updated Successfully")
