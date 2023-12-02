from random import randint
from typing import Annotated, List
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Form,
    UploadFile,
    File,
)
from sqlalchemy import or_, select, and_

from src.auth.exception import AccessDeniedException
from src.contract.exception import ContractNumberIsDuplicatedException
from src.contract.models import Contract
from src.core.config import settings
from src.log.models import LogType
from src.permission import permission_codes as permission

from src import deps
from src.agent.crud import agent as agent_crud
from src.log.crud import log as log_crud
from src.merchant.crud import merchant as merchant_crud
from src.organization.crud import organization as organization_crud
from src.agent.models import Agent, AgentLocation
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
    FieldOfWorkType,
    SellingType,
)
from src.position_request.schema import (
    PositionRequestRead,
    PositionRequestApproveIn,
    PositionRequestFilter,
    PositionRequestFilterOrderFild,
    PositionRequestUpdate,
)
from src.role.crud import role as role_crud
from src.schema import VerifyUserDep, IDRequest, ResultResponse
from src.user.crud import user as user_crud
from src.contract.crud import contract as contract_crud
from src.ability.crud import ability as ability_crud
from src.user.models import User
from src.utils.minio_client import MinioClient

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/position_request", tags=["position_request"])


# ---------------------------------------------------------------------------
@router.post(path="/update", response_model=ResultResponse)
async def update_position_request(
    *,
    db=Depends(deps.get_db),
    update_data: PositionRequestUpdate,
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_POSITION_REQUEST]),
    ),
) -> ResultResponse:
    """
    ! Update Position Request

    Parameters
    ----------
    db
    update_data
    current_user

    Returns
    -------
    res
        Result of operation

    Raises
    ------
    PositionRequestNotFoundException
    LocationNotFoundException
    ContractNumberIsDuplicatedException
    """
    # * Find position request
    position_request = await position_request_crud.verify_existence(
        db=db,
        position_request_id=update_data.where.id,
    )

    # * Verify location existence
    location = await location_crud.verify_existence(
        db=db,
        location_id=update_data.data.location_id,
    )

    # ! Verify contract number (duplicate)
    if position_request.contract.number != update_data.data.number:
        number_duplicated = await contract_crud.find_by_number(
            db=db,
            number=update_data.data.number,
            exception_number=position_request.contract.number,
        )
        if number_duplicated:
            raise ContractNumberIsDuplicatedException()

    # * Update Contract
    position_request.contract.number = update_data.data.number
    position_request.contract.name = update_data.data.name
    position_request.contract.signatory_name = update_data.data.signatory_name
    position_request.contract.signatory_position = update_data.data.signatory_position
    position_request.contract.employees_number = update_data.data.employee_count
    position_request.contract.field_of_work = update_data.data.field_of_work
    position_request.contract.postal_code = update_data.data.postal_code
    position_request.contract.tel = update_data.data.tel
    position_request.contract.address = update_data.data.address

    # * Create Position Request
    position_request.target_position = update_data.data.target_position
    position_request.location_id = location.id
    position_request.selling_type = update_data.data.selling_type
    position_request.name = update_data.data.name
    position_request.field_of_work = update_data.data.field_of_work
    position_request.postal_code = update_data.data.postal_code
    position_request.tel = update_data.data.tel
    position_request.received_money = update_data.data.received_money
    position_request.tracking_code = update_data.data.tracking_code
    position_request.address = update_data.data.address
    position_request.employee_count = update_data.data.employee_count
    position_request.geo = update_data.data.geo

    if position_request.target_position == PositionRequestType.AGENT:
        agent = await agent_crud.find_by_user_id(
            db=db,
            user_id=position_request.requester_user_id,
        )
        agent.location = location

        db.add(agent)
    elif position_request.target_position == PositionRequestType.ORGANIZATION:
        org = await organization_crud.find_by_user_id(
            db=db,
            user_id=position_request.requester_user_id,
        )
        org.location = location

        db.add(org)
    elif position_request.target_position == PositionRequestType.MERCHANT:
        merchant = await merchant_crud.find_by_user_id(
            db=db,
            user_id=position_request.requester_user_id,
        )
        merchant.field_of_work = update_data.data.field_of_work
        merchant.selling_type = update_data.data.selling_type
        merchant.geo = update_data.data.geo
        merchant.location = location

        db.add(merchant)

    db.add(position_request)
    await db.commit()
    await db.refresh(position_request)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.UPDATE_POSITION_REQUEST,
        user_id=current_user.id,
        detail="درخواست سمت با شماره {} با موفقیت توسط کاربر {} ویرایش شد".format(
            position_request.tracking_code,
            current_user.username,
        ),
    )

    return ResultResponse(result="Position request updated successfully")


# ---------------------------------------------------------------------------
@router.post(path="/create", response_model=PositionRequestRead)
async def create_position_request(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    requester_national_code: Annotated[str, Form()],
    target_position: Annotated[PositionRequestType, Form()],
    location_id: Annotated[UUID, Form()],
    number: Annotated[str, Form()],
    abilities_id_list: Annotated[list[UUID], Form()] = [],
    field_of_work: Annotated[FieldOfWorkType | None, Form()] = None,
    selling_type: Annotated[SellingType | None, Form()] = None,
    postal_code: Annotated[str, Form()],
    tel: Annotated[str, Form()],
    address: Annotated[str, Form()],
    employee_count: Annotated[int | None, Form()] = None,
    profit_rate: Annotated[int | None, Form()] = None,
    received_money: Annotated[str | None, Form()] = None,
    tracking_code: Annotated[str | None, Form()] = None,
    geo: Annotated[str | None, Form()] = None,
    name: Annotated[str, Form()],
    signatory_name: Annotated[str, Form()],
    signatory_position: Annotated[str, Form()],
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
    tel
    address
    received_money
    tracking_code
    employee_count
    abilities_id_list
    requester_national_code
    postal_code
    field_of_work
    minio
    target_position
    location_id
    selling_type
    number
    name
    signatory_name
    signatory_position
    contract_file
    geo
    current_user

    Returns
    -------
    position_request
        New Position Request

    Raises
    ------
    AccessDeniedException
    UserNotFoundException
    ContractNumberIsDuplicatedException
    AbilityNotFoundException
    """
    # * Verify creator existence and verify role
    if current_user.role.name != "نماینده" and current_user.role.name != "نماینده":
        raise AccessDeniedException()

    # * Verify requester existence and verify role
    requester_user = await user_crud.verify_existence_by_national_number(
        db=db,
        national_code=requester_national_code,
    )
    if not requester_user.role.name == "کاربر ساده":
        raise AccessDeniedException()

    # * verify abilities_id_list
    origin_agent_abilities = []
    if target_position == PositionRequestType.SALES_AGENT:
        for ability_id in abilities_id_list:
            ability = await ability_crud.verify_existence(db=db, ability_id=ability_id)
            origin_agent_abilities.append(ability)

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

    # ! Verify contract number (duplicate)
    number_duplicated = await contract_crud.find_by_number(db=db, number=number)
    if number_duplicated:
        raise ContractNumberIsDuplicatedException()

    # * Create Contract
    create_contract = Contract()
    create_contract.number = number
    create_contract.name = name
    create_contract.signatory_name = signatory_name
    create_contract.signatory_position = signatory_position
    create_contract.employees_number = employee_count
    create_contract.field_of_work = field_of_work
    create_contract.postal_code = postal_code
    create_contract.tel = tel
    create_contract.address = address
    create_contract.file_version_id = contract_file.version_id
    create_contract.file_name = contract_file.object_name

    # * Create Position Request
    code = generate_code = randint(100000, 999999)
    agent = await agent_crud.find_by_user_id(db=db, user_id=current_user.id)
    position_request = PositionRequest()
    if agent.parent_id:
        agent2 = await agent_crud.get(db=db, item_id=agent.parent_id)
        position_request.next_approve_user_id = agent2.user_id
    position_request.contract = create_contract
    position_request.code = code
    position_request.target_position = target_position
    position_request.location_id = location.id
    position_request.requester_user_id = requester_user.id
    position_request.creator_id = current_user.id
    position_request.selling_type = selling_type
    position_request.name = name
    position_request.creator_id = current_user.id
    position_request.field_of_work = field_of_work
    position_request.postal_code = postal_code
    position_request.tel = tel
    position_request.profit_rate = profit_rate
    position_request.received_money = received_money
    position_request.tracking_code = tracking_code
    position_request.address = address
    position_request.employee_count = employee_count
    position_request.geo = geo
    position_request.abilities = origin_agent_abilities

    db.add(position_request)
    db.add(create_contract)
    await db.commit()
    await db.refresh(position_request)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.CREATE_POSITION_REQUEST,
        user_id=current_user.id,
        detail="درخواست سمت با شماره {} با موفقیت توسط کاربر {} ایجاد شد".format(
            position_request.tracking_code,
            current_user.username,
        ),
    )

    return position_request


# ---------------------------------------------------------------------------
@router.put(path="/approve", response_model=PositionRequestRead)
async def approve_position_request(
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
    PositionRequestClosedException
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
            agent = await agent_crud.find_by_user_id(
                db=db,
                user_id=obj_current.next_approve_user_id,
            )
            obj_current.next_approve_user_id = (
                agent.parent_id if agent.parent_id else None
            )
        else:
            obj_current.status = PositionRequestStatusType.CLOSE
            obj_current.is_approve = False
            obj_current.reason = approve_data.reason
            obj_current.detail = approve_data.detail

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
                    new_agent.user_id = obj_current.requester_user_id
                    new_agent.locations = [location]
                    new_agent.parent = parent_agent
                    new_agent.is_main = True
                    new_agent.profit_rate = 40
                    new_agent.contract = obj_current.contract
                    agent_role = await role_crud.find_by_name(db=db, name="نماینده")
                    requester_user.role = agent_role

                    db.add(new_agent)
                elif obj_current.target_position == PositionRequestType.SALES_AGENT:
                    new_agent = Agent()
                    new_agent.user_id = obj_current.requester_user_id
                    new_agent.is_main = False
                    new_agent.abilities = obj_current.abilities
                    new_agent.location = location
                    new_agent.parent = parent_agent
                    new_agent.contract = obj_current.contract
                    agent_role = await role_crud.find_by_name(db=db, name="نماینده")
                    requester_user.role = agent_role

                    new_agent.profit_rate = await agent_crud.calculate_profit(
                        db=db,
                        number_of_ability=len(obj_current.abilities),
                    )

                    db.add(new_agent)
                elif obj_current.target_position == PositionRequestType.ORGANIZATION:
                    new_org = Organization()
                    new_org.location = location
                    new_org.agent_id = parent_agent.id
                    new_org.user_id = obj_current.requester_user_id
                    new_org.contract = obj_current.contract
                    org_role = await role_crud.find_by_name(db=db, name="سازمان")
                    requester_user.role = org_role

                    db.add(new_org)
                elif obj_current.target_position == PositionRequestType.MERCHANT:
                    new_merchant = Merchant()
                    new_merchant.user_id = obj_current.requester_user_id
                    new_merchant.field_of_work = obj_current.field_of_work
                    new_merchant.selling_type = obj_current.selling_type
                    new_merchant.agent_id = parent_agent.id
                    new_merchant.location = location
                    new_merchant.profit_rate = obj_current.profit_rate
                    new_merchant.geo = obj_current.geo
                    new_merchant.number = str(randint(100000, 999999))
                    new_merchant.contract = obj_current.contract
                    merchant_role = await role_crud.find_by_name(db=db, name="پذیرنده")
                    requester_user.role = merchant_role

                    db.add(new_merchant)
                obj_current.status = PositionRequestStatusType.CLOSE
                db.add(requester_user)

                # ! Close All another requester position
                open_requests = await position_request_crud.find_all_by_user_id(
                    db=db,
                    user_id=obj_current.requester_user_id,
                )
                for i in open_requests:
                    if not i.id == obj_current.id:
                        i.status = PositionRequestStatusType.CLOSE
                        i.is_approve = False
                        i.reason = "درخواست دیگری تایید شده است"
                        db.add(i)
            else:
                obj_current.status = PositionRequestStatusType.CLOSE
                obj_current.is_approve = False
                obj_current.reason = approve_data.reason
                obj_current.detail = approve_data.detail

        else:
            raise ApproveAccessDeniedException()

    db.add(obj_current)
    await db.commit()
    await db.refresh(obj_current)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        log_type=LogType.APPROVE_POSITION_REQUEST,
        user_id=current_user.id,
        detail="وضغیت درخواست سمت با شماره {} با موفقیت توسط کاربر {} ویرایش شد".format(
            obj_current.tracking_code,
            current_user.username,
        ),
    )

    return obj_current


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=PositionRequestRead)
async def find_position_request(
    *,
    db=Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_POSITION_REQUEST]),
    ),
    obj_data: IDRequest,
) -> PositionRequestRead:
    """
    ! Find Position Request

    Parameters
    ----------
    db
        Target database connection
    verify_data
        user's verified data
    obj_data
        Target position request id

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    PositionRequestNotFoundException
    AccessDeniedException
    """
    # * Verify position_request existence
    obj = await position_request_crud.verify_existence(
        db=db,
        position_request_id=obj_data.id,
    )
    if not verify_data.is_valid:
        is_requester = obj.requester_user_id == verify_data.user.id
        is_creator = obj.creator_id == verify_data.user.id
        if not is_creator and not is_requester:
            raise AccessDeniedException()

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[PositionRequestRead])
async def list_position_request(
    *,
    db=Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_POSITION_REQUEST]),
    ),
    filter_data: PositionRequestFilter,
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
    filter_data
        Filter data

    Returns
    -------
    obj_list
        found items
    """
    # * Prepare filter fields
    filter_data.field_of_work = (
        (PositionRequest.field_of_work == filter_data.field_of_work)
        if filter_data.field_of_work is not None
        else True
    )
    filter_data.target_position = (
        (PositionRequest.target_position == filter_data.target_position)
        if filter_data.target_position is not None
        else True
    )
    filter_data.is_approve = (
        (PositionRequest.is_approve == filter_data.is_approve)
        if filter_data.is_approve is not None
        else True
    )
    filter_data.status = (
        (PositionRequest.status == filter_data.status)
        if filter_data.status is not None
        else True
    )
    filter_data.position_request_name = (
        (PositionRequest.name.contains(filter_data.position_request_name))
        if filter_data.position_request_name
        else True
    )
    filter_data.name = (
        or_(
            User.first_name.contains(filter_data.name),
        )
        if filter_data.name is not None
        else True
    )
    filter_data.last_name = (
        or_(
            User.last_name.contains(filter_data.last_name),
        )
        if filter_data.last_name is not None
        else True
    )
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code is not None
        else True
    )

    # * Add filter fields
    query = (
        select(PositionRequest)
        .filter(
            and_(
                filter_data.field_of_work,
                filter_data.target_position,
                filter_data.is_approve,
                filter_data.status,
                filter_data.name,
                filter_data.last_name,
                filter_data.national_code,
            ),
        )
        .join(PositionRequest.requester_user)
        .order_by(PositionRequest.created_at.desc())
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == PositionRequestFilterOrderFild.field_of_work:
                query = query.order_by(PositionRequest.field_of_work.desc())
            elif field == PositionRequestFilterOrderFild.target_position:
                query = query.order_by(PositionRequest.target_position.desc())
            elif field == PositionRequestFilterOrderFild.is_approve:
                query = query.order_by(PositionRequest.is_approve.desc())
            elif field == PositionRequestFilterOrderFild.status:
                query = query.order_by(PositionRequest.status.desc())
            elif field == PositionRequestFilterOrderFild.created_at:
                query = query.order_by(PositionRequest.created_at.desc())
            elif field == PositionRequestFilterOrderFild.updated_at:
                query = query.order_by(PositionRequest.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == PositionRequestFilterOrderFild.field_of_work:
                query = query.order_by(PositionRequest.field_of_work.asc())
            elif field == PositionRequestFilterOrderFild.target_position:
                query = query.order_by(PositionRequest.target_position.asc())
            elif field == PositionRequestFilterOrderFild.is_approve:
                query = query.order_by(PositionRequest.is_approve.asc())
            elif field == PositionRequestFilterOrderFild.status:
                query = query.order_by(PositionRequest.status.asc())
            elif field == PositionRequestFilterOrderFild.created_at:
                query = query.order_by(PositionRequest.created_at.asc())
            elif field == PositionRequestFilterOrderFild.updated_at:
                query = query.order_by(PositionRequest.updated_at.asc())

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
@router.post(path="/list/must_approve", response_model=List[PositionRequestRead])
async def get_must_approve_position_request(
    *,
    db=Depends(deps.get_db),
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_POSITION_REQUEST]),
    ),
    skip: int = 0,
    limit: int = 20,
    filter_data: PositionRequestFilter,
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
    filter_data
        Filter data

    Returns
    -------
    obj_list
        found items
    """
    # * Prepare filter fields
    filter_data.field_of_work = (
        (PositionRequest.field_of_work == filter_data.field_of_work)
        if filter_data.field_of_work is not None
        else True
    )
    filter_data.target_position = (
        (PositionRequest.target_position == filter_data.target_position)
        if filter_data.target_position is not None
        else True
    )
    filter_data.is_approve = (
        (PositionRequest.is_approve == filter_data.is_approve)
        if filter_data.is_approve is not None
        else True
    )
    filter_data.status = (
        (PositionRequest.status == filter_data.status)
        if filter_data.status is not None
        else True
    )
    filter_data.position_request_name = (
        (PositionRequest.name.contains(filter_data.position_request_name))
        if filter_data.position_request_name
        else True
    )
    filter_data.name = (
        or_(
            User.first_name.contains(filter_data.name),
        )
        if filter_data.name is not None
        else True
    )
    filter_data.last_name = (
        or_(
            User.last_name.contains(filter_data.last_name),
        )
        if filter_data.last_name is not None
        else True
    )
    filter_data.national_code = (
        (User.national_code.contains(filter_data.national_code))
        if filter_data.national_code is not None
        else True
    )

    # * Add filter fields
    query = (
        select(PositionRequest)
        .filter(
            and_(
                filter_data.field_of_work,
                filter_data.target_position,
                filter_data.is_approve,
                filter_data.status,
                filter_data.name,
                filter_data.last_name,
                filter_data.national_code,
            ),
        )
        .join(PositionRequest.requester_user)
        .order_by(PositionRequest.created_at.desc())
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == PositionRequestFilterOrderFild.field_of_work:
                query = query.order_by(PositionRequest.field_of_work.desc())
            elif field == PositionRequestFilterOrderFild.target_position:
                query = query.order_by(PositionRequest.target_position.desc())
            elif field == PositionRequestFilterOrderFild.is_approve:
                query = query.order_by(PositionRequest.is_approve.desc())
            elif field == PositionRequestFilterOrderFild.status:
                query = query.order_by(PositionRequest.status.desc())
            elif field == PositionRequestFilterOrderFild.created_at:
                query = query.order_by(PositionRequest.created_at.desc())
            elif field == PositionRequestFilterOrderFild.updated_at:
                query = query.order_by(PositionRequest.updated_at.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == PositionRequestFilterOrderFild.field_of_work:
                query = query.order_by(PositionRequest.field_of_work.asc())
            elif field == PositionRequestFilterOrderFild.target_position:
                query = query.order_by(PositionRequest.target_position.asc())
            elif field == PositionRequestFilterOrderFild.is_approve:
                query = query.order_by(PositionRequest.is_approve.asc())
            elif field == PositionRequestFilterOrderFild.status:
                query = query.order_by(PositionRequest.status.asc())
            elif field == PositionRequestFilterOrderFild.created_at:
                query = query.order_by(PositionRequest.created_at.asc())
            elif field == PositionRequestFilterOrderFild.updated_at:
                query = query.order_by(PositionRequest.updated_at.asc())

    # * Not Have permissions
    if not verify_data.is_valid:
        query = query.where(
            PositionRequest.next_approve_user_id == verify_data.user.id,
        )
    else:
        query = query.where(
            and_(
                PositionRequest.next_approve_user_id.is_(None),
                PositionRequest.status == PositionRequestStatusType.OPEN,
            ),
        )

    obj_list = await position_request_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        query=query,
    )
    return obj_list
