from typing import List, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy import select, or_, and_

from src import deps
from src.contract.crud import contract as contract_crud
from src.contract.exception import ContractNotFoundException
from src.contract.models import Contract
from src.contract.schema import ContractRead, ContractFilter, ContractFilterOrderFild
from src.core.config import settings
from src.schema import IDRequest, VerifyUserDep, ResultResponse
from src.permission import permission_codes as permission
from src.user.models import User
from src.utils.minio_client import MinioClient

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/contract", tags=["contract"])


# ---------------------------------------------------------------------------
@router.put(path="/update/file", response_model=ResultResponse)
async def update_contract_file(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_POSITION_REQUEST]),
    ),
    contract_id: Annotated[UUID, Form()],
    minio: MinioClient = Depends(deps.minio_auth),
    contract_file: Annotated[UploadFile, File()],
) -> ResultResponse:
    # * Find position request
    contract = await contract_crud.verify_existence(db=db, contract_id=contract_id)

    if contract.file_version_id:
        minio.client.remove_object(
            bucket_name=settings.MINIO_CONTRACT_BUCKET,
            object_name=contract.file_name,
            version_id=contract.file_version_id,
        )
        contract.file_name = None
        contract.file_version_id = None

    # * Save Contract File
    contract_file = minio.client.put_object(
        data=contract_file.file,
        object_name=contract_file.filename,
        bucket_name=settings.MINIO_CONTRACT_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )

    contract.file_version_id = contract_file.version_id
    contract.file_name = contract_file.object_name
    db.add(contract)
    await db.commit()
    return ResultResponse(result="Contract Updated Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=ContractRead)
async def find_contract(
    *,
    db=Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_CONTRACT]),
    ),
    obj_data: IDRequest,
) -> ContractRead:
    """
    ! Find Contract

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    obj_data
        Target Contract's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    ContractNotFoundException
    """
    # ? Verify contract existence
    obj = await contract_crud.verify_existence(db=db, contract_id=obj_data.id)

    # * Not Have permissions
    if not verify_data.is_valid:
        is_requester = obj.position_request.requester_user_id == verify_data.user.id
        is_creator = obj.position_request.creator_id == verify_data.user.id
        if not is_requester or not is_creator:
            raise ContractNotFoundException()

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[ContractRead])
async def get_contract(
    *,
    db=Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_CONTRACT]),
    ),
    filter_data: ContractFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[ContractRead]:
    """
    ! Get All Contract

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
        List of ability
    """
    # * Prepare filter fields
    filter_data.number = (
        (Contract.number.contains(filter_data.number)) if filter_data.number else True
    )

    # * Add filter fields
    query = select(Contract).filter(
        and_(
            filter_data.number,
        ),
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == ContractFilterOrderFild.number:
                query = query.order_by(Contract.number.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == ContractFilterOrderFild.number:
                query = query.order_by(Contract.number.asc())

    # * Not Have permissions
    if not verify_data.is_valid:
        query = query.where(
            or_(
                Contract.position_request.requester_user_id == verify_data.user.id,
                Contract.position_request.creator_id == verify_data.user.id,
            ),
        )
    obj_list = await contract_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return obj_list
