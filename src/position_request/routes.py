from typing import Annotated, List
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)
from sqlalchemy import or_, select

from src.auth.exception import AccessDeniedException
from src.contract.models import Contract
from src.permission import permission_codes as permission

from src import deps
from src.agent.crud import agent as agent_crud
from src.agent.models import Agent
from src.core.config import settings
from src.location.crud import location as location_crud
from src.merchant.models import Merchant
from src.organization.models import Organization
from src.position_request.crud import position_request as position_request_crud
from src.position_request.exception import (
    ApproveAccessDeniedException,
    PositionRequestClosedException,
)
from src.position_request.models import (
    PositionRequest,
    PositionRequestStatusType,
    PositionRequestType,
)
from src.position_request.schema import (
    PositionRequestRead,
    PositionRequestApproveIn,
)
from src.role.crud import role as role_crud
from src.schema import VerifyUserDep, IDRequest
from src.user.crud import user as user_crud
from src.user.models import User
from src.utils.minio_client import MinioClient

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/position_request", tags=["position_request"])


# ---------------------------------------------------------------------------
@router.post(path="/create", response_model=PositionRequestRead)
async def create_position_request(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    requester_username: Annotated[str | None, Form()] = None,
    target_position: Annotated[PositionRequestType, Form()],
    location_id: Annotated[UUID, Form()],
    number: Annotated[str, Form()],
    name: Annotated[str | None, Form()] = None,
    signatory_name: Annotated[str | None, Form()] = None,
    signatory_position: Annotated[str | None, Form()] = None,
    employees_number: Annotated[int | None, Form()] = None,
    contract_file: Annotated[UploadFile, File()],
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CREATE_POSITION_REQUEST]),
    ),
) -> PositionRequestRead:
    """
    ! Create Position Request [Big Api]

    Parameters
    ----------
    db
    minio
    requester_username
    target_position
    location_id
    number
    name
    signatory_name
    signatory_position
    employees_number
    contract_file
    current_user

    Returns
    -------
    position_request
        New Position Request

    Raises
    ------
    AccessDeniedException
    UserNotFoundException
    """
    # * Verify creator existence and verify role
    creator_user = await user_crud.get(
        db=db,
        item_id=current_user.id,
    )
    if not creator_user.role.name == "نماینده":
        raise AccessDeniedException()

    # * Verify requester existence and verify role
    requester_user = await user_crud.verify_existence_by_username(
        db=db,
        username=requester_username,
    )
    if not requester_user.role.name == "کاربر ساده":
        raise AccessDeniedException()

    # * Verify location existence
    location = await location_crud.verify_existence(
        db=db,
        location_id=location_id,
    )

    # * Save Contract File
    contract_file = minio.client.put_object(
        data=contract_file.file,
        object_name=contract_file.filename,
        bucket_name=settings.MINIO_CONTRACT_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    # * Create Contract
    create_contract = Contract()
    create_contract.number = number
    create_contract.name = name
    create_contract.signatory_name = signatory_name
    create_contract.signatory_position = signatory_position
    create_contract.employees_number = employees_number
    create_contract.file_version_id = contract_file.version_id
    create_contract.file_name = contract_file.object_name

    # * Create Position Request
    code = await position_request_crud.generate_code(db=db)
    agent = await agent_crud.find_by_user_id(db=db, user_id=creator_user.id)
    position_request = PositionRequest()
    position_request.contract = create_contract
    position_request.code = code
    position_request.target_position = target_position
    position_request.next_approve_user_id = agent.parent_id
    position_request.location_id = location.id
    position_request.requester_user_id = requester_user.id
    position_request.creator_id = current_user.id

    db.add(position_request)
    db.add(create_contract)
    await db.commit()
    await db.refresh(position_request)
    return position_request


# ---------------------------------------------------------------------------
@router.put(path="/approve", response_model=PositionRequestRead)
async def update_position_request(
    *,
    db=Depends(deps.get_db),
    approve_data: PositionRequestApproveIn,
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.APPROVE_POSITION_REQUEST]),
    ),
) -> PositionRequestRead:
    """
    ! Approve PositionRequest

    Parameters
    ----------
    db
        Target database connection
    approve_data
        Necessary data for approve request
    current_user
        Requester User

    Returns
    -------
    updated position request

    Raises
    ------
    PositionRequestNotFoundException
    ApproveAccessDeniedException
    """
    # * Verify position_request existence
    obj_current = (
        await position_request_crud.verify_not_finished_position_request_existence(
            db=db,
            position_request_id=approve_data.position_request_id,
        )
    )

    if obj_current.status == PositionRequestStatusType.CLOSE:
        raise PositionRequestClosedException()

    # * Have next level for approve
    if (
        obj_current.next_approve_user
        and obj_current.status == PositionRequestStatusType.OPEN
    ):
        # ! Is Accept ?
        if approve_data.is_approve:
            # * Verify requester = next approve person existence
            if obj_current.next_approve_user_id != current_user.id:
                raise ApproveAccessDeniedException()
            agent = await agent_crud.get_agent_with_user_id(
                db=db,
                user_id=obj_current.next_approve_user_id,
            )
            obj_current.next_approve_user_id = (
                agent.parent_id if agent.parent_id else None
            )
        else:
            obj_current.status = PositionRequestStatusType.CLOSE

    # ? must approve from admin
    elif obj_current.status == PositionRequestStatusType.OPEN:
        admin_role = await role_crud.find_by_name(db=db, name="ادمین")
        if current_user.role == admin_role:
            # ! Is Accept ?
            if approve_data.is_approve:
                obj_current.is_approve = True
                requester_user = await user_crud.get(
                    db=db,
                    item_id=obj_current.requester_user_id,
                )
                location = await location_crud.get(
                    db=db,
                    item_id=obj_current.location_id,
                )
                parent_agent = await agent_crud.find_by_user_id(
                    db=db,
                    user_id=obj_current.creator.id,
                )

                # ? Change user role
                if obj_current.target_position == PositionRequestType.AGENT:
                    new_agent = Agent()
                    new_agent.agent_user_id = obj_current.requester_user_id
                    new_agent.location = location
                    new_agent.parent = parent_agent
                    agent_role = await role_crud.find_by_name(db=db, name="نماینده")
                    requester_user.role = agent_role

                    db.add(new_agent)
                elif obj_current.target_position == PositionRequestType.ORGANIZATION:
                    new_org = Organization()
                    new_org.location = location
                    new_org.agent.agent_user_id = parent_agent
                    new_org.user_organization_id = obj_current.requester_user_id
                    org_role = await role_crud.find_by_name(db=db, name="سازمان")
                    requester_user.role = org_role

                    db.add(new_org)
                elif obj_current.target_position == PositionRequestType.MERCHANT:
                    new_merchant = Merchant()
                    new_merchant.user_id = obj_current.requester_user_id
                    new_merchant.agent.agent_user_id = parent_agent
                    new_merchant.location = location
                    merchant_role = await role_crud.find_by_name(db=db, name="پذیرنده")
                    requester_user.role = merchant_role

                    db.add(new_merchant)
                db.add(requester_user)
            else:
                obj_current.status = PositionRequestStatusType.CLOSE
                obj_current.is_approve = False

        else:
            raise ApproveAccessDeniedException()

    db.add(obj_current)
    await db.commit()
    await db.refresh(obj_current)
    return obj_current


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=PositionRequestRead)
async def find_position_request(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_POSITION_REQUEST]),
    ),
    obj_data: IDRequest,
) -> PositionRequestRead:
    """
    ! Find Position Request

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target position request id

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    PositionRequestNotFoundException
    """
    # * Verify position_request existence
    obj = await position_request_crud.verify_existence(
        db=db,
        position_request_id=obj_data.id,
    )
    return obj


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[PositionRequestRead])
async def get_list_position_request(
    *,
    db=Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_POSITION_REQUEST]),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[PositionRequestRead]:
    """
    ! Get All PositionRequest

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

    Returns
    -------
    obj_list
        found items
    """
    query = select(PositionRequest)
    # * Not Have permissions
    if not verify_data.is_valid:
        query = query.where(
            or_(
                PositionRequest.requester_user_id == verify_data.user.id,
                PositionRequest.creator_id == verify_data.user.id,
            ),
        )
    obj_list = await position_request_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list


# ---------------------------------------------------------------------------
@router.post(path="/list/my/must_approve", response_model=List[PositionRequestRead])
async def get_must_approve_position_request(
    *,
    db=Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_POSITION_REQUEST]),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[PositionRequestRead]:
    """
    ! Get All Position Request that must be approved

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

    Returns
    -------
    obj_list
        found items
    """
    query = select(PositionRequest)
    # * Not Have permissions
    if not verify_data.is_valid:
        query = query.where(
            PositionRequest.next_approve_user_id == verify_data.user.id,
        )
    else:
        query = query.where(
            PositionRequest.next_approve_user_id.is_(None),
            PositionRequest.status == PositionRequestStatusType.OPEN,
        )

    obj_list = await position_request_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list
