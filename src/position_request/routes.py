from random import randint
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

from src import deps
from src.agent.crud import agent as agent_crud
from src.agent.models import Agent
from src.contract.crud import contract as contract_crud
from src.core.config import settings
from src.location.crud import location as location_crud
from src.merchant.models import Merchant
from src.organization.models import Organization
from src.position_request.crud import position_request as position_request_crud
from src.position_request.exception import ApproveAccessDeniedException
from src.position_request.models import (
    PositionRequest,
    PositionRequestStatusType,
    PositionRequestType,
)
from src.position_request.schema import (
    PositionRequestCreate,
    PositionRequestRead,
)
from src.role.crud import role as role_crud
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
    create_data: PositionRequestCreate,
    minio: MinioClient = Depends(deps.minio_auth),
    requester_user_name: Annotated[str | None, Form()] = None,
    target_position: Annotated[PositionRequestType, Form()],
    location_id: Annotated[UUID, Form()],
    number: Annotated[str, Form()],
    name: Annotated[str | None, Form()] = None,
    signatory_name: Annotated[str | None, Form()] = None,
    signatory_position: Annotated[str | None, Form()] = None,
    employees_number: Annotated[int | None, Form()] = None,
    contract_file: Annotated[UploadFile, File()],
    current_user: User = Depends(deps.get_current_user()),
) -> PositionRequestRead:
    """
    ! Create PositionRequest with permission

    Parameters
    ----------
    db
        Target database connection
    create_data
        Necessary data for create position_request
    current_user
        Requester User

    Returns
    -------
    obj
        New Position request

    Raises
    ------
    UserNotFoundException
    LocationNotFoundException
    """

    # ? Verify requester user existence
    requester_user = await user_crud.verify_existence_by_username(
        db=db,
        username=create_data.requester_user_name,
    )
    # ? Verify location user existence
    location = await location_crud.verify_existence(
        db=db,
        location_id=create_data.location_id,
    )
    minio.client.put_object(
        data=contract_file.file,
        object_name=contract_file.filename,
        bucket_name=settings.MINIO_DEFAULT_BUCKET,
        length=-1,
        part_size=10 * 1024 * 1024,
    )
    # ? Create Contract
    contract = await contract_crud.create(db=db, obj_in=create_data.contract)
    # ? agent => location's parent agent todo: complete this code
    agent = await agent_crud.get(db=db, id=location.agent_id)
    if agent:
        agent = agent.agent_user_id
    # ? Create Object
    obj = PositionRequest()
    obj.contract = contract
    obj.target_position = create_data.target_position
    obj.next_approve_user_id = agent
    obj.location_id = location.id
    obj.requester_user_id = requester_user.id
    obj.creator_id = current_user.id

    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# ---------------------------------------------------------------------------
@router.post(path="/create/personal", response_model=PositionRequestRead)
async def create_personal_position_request(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    create_data: PositionRequestCreate,
) -> PositionRequestRead:
    """
    ! Create PositionRequest personal

    Parameters
    ----------
    db
        Target database connection
    create_data
        Necessary data for create position_request
    current_user
        Requester User

    Returns
    -------
    obj
        New Position request

    Raises
    ------
    LocationNotFoundException
    """
    # ? Verify location user existence
    location = await location_crud.verify_location_existence(
        db=db,
        id=create_data.location_id,
    )
    # ? Create Contract
    contract = await contract_crud.create(db=db, obj_in=create_data.contract)
    # ? agent => location's parent agent todo: complete this code
    obj = PositionRequest()
    if location.agent_id:
        next_user_agent = await agent_crud.verify_agent_existence(
            db=db,
            id=location.agent_id,
        )
        obj.next_approve_user_id = next_user_agent.agent_user_id
    else:
        obj.next_approve_user_id = None

    obj.contract = contract
    obj.target_position = create_data.target_position
    obj.location_id = location.id
    obj.requester_user_id = current_user.id
    obj.creator_id = current_user.id

    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# ---------------------------------------------------------------------------
@router.put(path="/approve/{item_id}/{accept}", response_model=PositionRequestRead)
async def update_position_request(
    *,
    db=Depends(deps.get_db),
    item_id: UUID,
    accept: bool,
    current_user: User = Depends(deps.get_current_user()),
) -> PositionRequestRead:
    """
    ! Approve PositionRequest

    :param item_id: sad
    :param current_user: Requester User
    :param db: Target database connection
    :return: Updated position_request
    """
    # ? Verify position_request existence
    obj_current = (
        await position_request_crud.verify_not_finished_position_request_existence(
            db=db,
            position_request_id=item_id,
        )
    )

    # ? have nxt level for approve
    if (
        obj_current.next_approve_user
        and obj_current.status == PositionRequestStatusType.OPEN
    ):
        # ! Is Accept ?
        if accept:
            # ? Verify requester = next approve person existence
            if obj_current.next_approve_user_id != current_user.id:
                raise ApproveAccessDeniedException()

            agent = await agent_crud.get_agent_with_user_id(
                db=db,
                user_id=obj_current.next_approve_user_id,
            )
            location = await location_crud.get_location_with_agent_id(
                db=db,
                agent_id=agent.id,
            )
            if location.parent_id:
                location = await location_crud.verify_location_existence(
                    db=db,
                    id=location.parent_id,
                )
                obj_current.next_approve_user_id = location.agent_id
            else:
                obj_current.next_approve_user_id = None
        else:
            obj_current.status = PositionRequestStatusType.CLOSE

    # ? must approve from admin
    elif obj_current.status == PositionRequestStatusType.OPEN:
        admin_role = await role_crud.find_by_name(db=db, name="ادمین")
        if current_user.role == admin_role:
            # ! Is Accept ?
            if accept:
                obj_current.is_approve = True
                requester_user = await user_crud.get(
                    db=db,
                    id=obj_current.requester_user_id,
                )
                location = await location_crud.get(db=db, id=obj_current.location_id)

                # ? Change user role
                if obj_current.target_position == PositionRequestType.AGENT:
                    new_agent = Agent()
                    new_agent.agent_user_id = obj_current.requester_user_id
                    new_agent.location = location

                    agent_role = await role_crud.find_by_name(db=db, name="نماینده")
                    requester_user.role = agent_role

                    db.add(requester_user)
                    db.add(new_agent)
                    await db.commit()
                elif obj_current.target_position == PositionRequestType.ORGANIZATION:
                    new_org = Organization()
                    new_org.location = location
                    new_org.user_organization_id = obj_current.requester_user_id

                    org_role = await role_crud.find_by_name(db=db, name="سازمان")
                    requester_user.role = org_role

                    db.add(requester_user)
                    db.add(new_org)
                    await db.commit()

                elif obj_current.target_position == PositionRequestType.ACCEPTOR:
                    new_org = Merchant()
                    new_org.user_id = obj_current.requester_user_id
                    new_org.location = location
                    new_org.number = randint(100000, 999999)

                    org_role = await role_crud.find_by_name(db=db, name="پذیرنده")
                    requester_user.role = org_role

                    db.add(requester_user)
                    db.add(new_org)
                    await db.commit()

            else:
                obj_current.status = PositionRequestStatusType.CLOSE

        else:
            raise ApproveAccessDeniedException()

    db.add(obj_current)
    await db.commit()
    return obj_current


# ---------------------------------------------------------------------------
@router.get(path="/get/{item_id}", response_model=PositionRequestRead)
async def get_position_request(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    item_id: UUID,
) -> PositionRequestRead:
    """
    ! Get one PositionRequest

    :param current_user: Requester User
    :param db: Target database connection
    :param item_id: Target PositionRequest's ID
    :return: Found Item
    """
    # ? Verify position_request existence
    obj = await position_request_crud.verify_position_request_existence(
        db=db,
        id=item_id,
    )

    return obj


# ---------------------------------------------------------------------------
@router.get(path="/list", response_model=List[PositionRequestRead])
async def get_list_position_request(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    skip: int = 0,
    limit: int = 20,
) -> List[PositionRequestRead]:
    """
    ! Get All PositionRequest

    :param current_user: Required permissions
    :param limit: Pagination limit
    :param skip: Pagination skip
    :param db: Target database connection
    :return: List of ability
    """
    obj_list = await position_request_crud.get_multi(db=db, skip=skip, limit=limit)
    return obj_list


# ---------------------------------------------------------------------------
@router.get(path="/list/my/must_approve", response_model=List[PositionRequestRead])
async def get_must_approve_position_request(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    skip: int = 0,
    limit: int = 20,
) -> List[PositionRequestRead]:
    """
    ! Get All Position Request

    :param current_user: Required permissions
    :param limit: Pagination limit
    :param skip: Pagination skip
    :param db: Target database connection
    :return: List of ability
    """
    query = select(PositionRequest).where(
        PositionRequest.next_approve_user_id == current_user.id,
    )
    obj_list = await position_request_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list


# ---------------------------------------------------------------------------
@router.get(path="/list/admin/must_approve", response_model=List[PositionRequestRead])
async def get_must_approve_addmin_position_request(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    skip: int = 0,
    limit: int = 20,
) -> List[PositionRequestRead]:
    """
    ! Get All Position Request

    :param current_user: Required permissions
    :param limit: Pagination limit
    :param skip: Pagination skip
    :param db: Target database connection
    :return: List of ability
    """
    query = select(PositionRequest).where(
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


# ---------------------------------------------------------------------------
@router.get(path="/list/my", response_model=List[PositionRequestRead])
async def get_my_position_requests(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    skip: int = 0,
    limit: int = 20,
) -> List[PositionRequestRead]:
    """
    ! Get All Position Request

    :param current_user: Required permissions
    :param limit: Pagination limit
    :param skip: Pagination skip
    :param db: Target database connection
    :return: List of ability
    """
    query = select(PositionRequest).where(
        or_(
            PositionRequest.requester_user_id == current_user.id,
            PositionRequest.creator_id == current_user.id,
        ),
    )
    obj_list = await position_request_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list
