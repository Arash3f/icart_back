from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.agent.models import Agent
from src.merchant.models import Merchant
from src.organization.models import Organization
from src.position_request.models import (
    PositionRequest,
    PositionRequestType,
    PositionRequestStatusType,
)
from src.important_data.schema import (
    SystemAdditionalInfo,
    SystemRequestInfo,
)
from src.user.models import User
from src.user_request.models import UserRequest
from src.permission import permission_codes as permission

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/important_data", tags=["important_data"])


# ---------------------------------------------------------------------------
# @router.put(path="/update", response_model=ImportantDataRead)
# async def update_important_data(
#     *,
#     db=Depends(deps.get_db),
#     current_user: User = Depends(
#         deps.get_current_user_with_permissions([permission.UPDATE_IMPORTANT_DATA]),
#     ),
#     update_data: ImportantDataUpdate,
# ) -> ImportantDataRead:
#     """
#     ! Update ImportantData
#
#     Parameters
#     ----------
#     db
#         Target database connection
#     current_user
#         Requester User
#     update_data
#          Necessary data for update important_data
#
#     Returns
#     -------
#     obj
#         Updated important_data
#
#     Raises
#     ------
#     ImportantDataNotFoundException
#     """
#     # * Verify important_data existence
#     obj_current = await important_data_crud.verify_existence(
#         db=db,
#         user_crypto_id=update_data.where.id,
#     )
#     # * Update
#     obj = await important_data_crud.update(
#         db=db,
#         obj_current=obj_current,
#         obj_new=update_data.data,
#     )
#     return obj
#
#
# # ---------------------------------------------------------------------------
# @router.post(path="/list", response_model=List[ImportantDataRead])
# async def get_important_data_list(
#     *,
#     db=Depends(deps.get_db),
#     current_user: User = Depends(
#         deps.get_current_user_with_permissions([permission.VIEW_IMPORTANT_DATA]),
#     ),
#     skip: int = 0,
#     limit: int = 20,
# ) -> List[ImportantDataRead]:
#     """
#     ! Get All Important Data
#
#     Parameters
#     ----------
#     db
#         Target database connection
#     current_user
#         Requester User
#     skip
#         Pagination skip
#     limit
#         Pagination limit
#
#     Returns
#     -------
#     obj_list
#         All Important Data
#     """
#     obj_list = await important_data_crud.get_multi(db=db, skip=skip, limit=limit)
#     return obj_list


# ---------------------------------------------------------------------------
@router.get("/additional_info", response_model=SystemAdditionalInfo)
async def get_additional_info(
    *,
    db: AsyncSession = Depends(deps.get_db),
) -> SystemAdditionalInfo:
    """
    * Get General information about system users

    Parameters
    ----------
    db
        database connection

    Returns
    -------
    res
        result of operation
    """
    response = await db.execute(
        select(func.count()).select_from(User),
    )
    all_users = response.scalar()

    response = await db.execute(
        select(func.count())
        .select_from(Agent)
        .filter(
            Agent.is_main == True,
        ),
    )
    agent_count = response.scalar()

    response = await db.execute(
        select(func.count())
        .select_from(Agent)
        .filter(
            Agent.is_main == False,
        ),
    )
    sales_agent_count = response.scalar()

    response = await db.execute(
        select(func.count()).select_from(Organization),
    )
    organization_count = response.scalar()

    response = await db.execute(
        select(func.count()).select_from(Merchant),
    )
    merchant_count = response.scalar()

    user_count = (
        all_users
        - agent_count
        - organization_count
        - merchant_count
        - sales_agent_count
    )

    return SystemAdditionalInfo(
        agent_count=agent_count,
        organization_count=organization_count,
        merchant_count=merchant_count,
        user_count=user_count,
        sales_agent_count=sales_agent_count,
    )


# ---------------------------------------------------------------------------
@router.get("/request/info", response_model=SystemRequestInfo)
async def get_request_info(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_POSITION_REQUEST]),
    ),
) -> SystemRequestInfo:
    """
    * Get General information about system requests

    Parameters
    ----------
    db
        database connection
    current_user
        Requester User

    Returns
    -------
    res
        result of operation
    """
    response = await db.execute(
        select(func.count())
        .select_from(PositionRequest)
        .filter(
            PositionRequest.target_position == PositionRequestType.AGENT,
            PositionRequest.status == PositionRequestStatusType.OPEN,
        ),
    )
    new_agent_count = response.scalar()

    response = await db.execute(
        select(func.count())
        .select_from(PositionRequest)
        .filter(
            PositionRequest.target_position == PositionRequestType.ORGANIZATION,
            PositionRequest.status == PositionRequestStatusType.OPEN,
        ),
    )
    new_organization_count = response.scalar()

    response = await db.execute(
        select(func.count())
        .select_from(PositionRequest)
        .filter(
            PositionRequest.target_position == PositionRequestType.MERCHANT,
            PositionRequest.status == PositionRequestStatusType.OPEN,
        ),
    )
    new_merchant_count = response.scalar()

    response = await db.execute(
        select(func.count())
        .select_from(PositionRequest)
        .filter(
            PositionRequest.target_position == PositionRequestType.SALES_AGENT,
            PositionRequest.status == PositionRequestStatusType.OPEN,
        ),
    )
    new_sales_agent_count = response.scalar()

    response = await db.execute(
        select(func.count())
        .select_from(UserRequest)
        .filter(
            UserRequest.status == False,
        ),
    )
    new_user_count = response.scalar()

    return SystemAdditionalInfo(
        new_agent_count=new_agent_count,
        new_organization_count=new_organization_count,
        new_merchant_count=new_merchant_count,
        new_user_count=new_user_count,
        new_sales_agent_count=new_sales_agent_count,
    )
