from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, func

from src import deps
from src.ability.crud import ability as ability_crud
from src.agent.crud import agent as agent_crud
from src.location.models import Location
from src.user.crud import user as user_crud
from src.agent.models import Agent
from src.agent.schema import (
    AgentFilter,
    AgentFilterOrderFild,
    AgentRead,
    AgentUpdate,
    IncomeFromUser,
)
from src.schema import IDRequest
from src.transaction.models import Transaction
from src.user.models import User
from src.permission import permission_codes as permission

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/agent", tags=["agent"])


# ---------------------------------------------------------------------------
@router.put(path="/update", response_model=AgentRead)
async def update_agent(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_AGENT]),
    ),
    update_data: AgentUpdate,
) -> AgentRead:
    """
    ! Update Agent

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user object
    update_data
        Necessary data for update agent

    Returns
    -------
    agent
        Updated agent

    Raises
    ------
    AbilityNotFoundException
    AgentNotFoundException
    """
    # * verify abilities existence
    ability_list = await ability_crud.verify_list_existence(
        db=db,
        list_ids=update_data.data.abilities,
    )
    #  * Verify agent existence
    obj_current = await agent_crud.verify_existence(
        db=db,
        user_crypto_id=update_data.where.id,
    )
    # * Update agent
    obj_current.abilities = ability_list
    db.add(obj_current)
    await db.commit()

    # ? update agent interest and main filed
    agent = await agent_crud.update_agents_profit_rate(
        db=db,
        target_agent=obj_current,
    )

    return agent


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=AgentRead)
async def find_agent(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_AGENT]),
    ),
    obj_data: IDRequest,
) -> AgentRead:
    """
    ! Find Agent

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user object
    obj_data
        Target Agent's ID

    Returns
    -------
    agent
        Found Item

    Raises
    ------
    AgentNotFoundException
    """
    # * Verify agent existence
    agent = await agent_crud.verify_existence(db=db, agent_id=obj_data.id)

    return agent


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[AgentRead])
async def get_agent_list(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    filter_data: AgentFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[AgentRead]:
    """
    ! Get All Agent

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user object
    skip
        Pagination skip
    limit
        Pagination limit
    filter_data
        Filter data

    Returns
    -------
    agent_list
        List of ability
    """
    # * Prepare filter fields
    filter_data.is_main = (
        (Agent.is_main == True) if filter_data.is_main is not None else True
    )
    filter_data.first_name = (
        (Agent.user.mapper.class_.first_name.contains(filter_data.first_name))
        if filter_data.first_name is not None
        else True
    )
    filter_data.last_name = (
        (Agent.user.mapper.class_.last_name.contains(filter_data.last_name))
        if filter_data.last_name is not None
        else True
    )
    filter_data.national_code = (
        (Agent.user.mapper.class_.national_code.contains(filter_data.national_code))
        if filter_data.national_code is not None
        else True
    )
    filter_data.location_id = (
        (Agent.locations.any(Location.id == filter_data.location_id))
        if filter_data.is_main is not None
        else True
    )
    filter_data.phone_number = (
        (Agent.user.mapper.class_.phone_number.contains(filter_data.phone_number))
        if filter_data.phone_number is not None
        else True
    )
    # * Add filter fields
    query = select(Agent).filter(
        and_(
            filter_data.is_main,
            filter_data.first_name,
            filter_data.last_name,
            filter_data.national_code,
            filter_data.location_id,
            filter_data.phone_number,
        ),
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == AgentFilterOrderFild.is_main:
                query = query.order_by(Agent.is_main.desc())
            elif field == AgentFilterOrderFild.profit_rate:
                query = query.order_by(Agent.profit_rate.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == AgentFilterOrderFild.is_main:
                query = query.order_by(Agent.is_main.asc())
            elif field == AgentFilterOrderFild.profit_rate:
                query = query.order_by(Agent.profit_rate.asc())
    # * Find All agent with filters
    agent_list = await agent_crud.get_multi(db=db, skip=skip, limit=limit, query=query)

    return agent_list


# ---------------------------------------------------------------------------
@router.post(path="/income_from", response_model=List[IncomeFromUser])
async def get_income_from(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    filter_data: IDRequest,
) -> List[IncomeFromUser]:
    """
    ! Calculate Income from user by user id

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester user object
    filter_data
        Filter data

    Returns
    -------
    result
        Income from user
    """
    user = await user_crud.verify_existence(db=db, user_id=filter_data.id)
    response_data: list[IncomeFromUser] = []
    query = (
        select(Transaction.value_type, func.sum(Transaction.value))
        .select_from(Transaction)
        .filter(
            and_(
                Transaction.intermediary_id == user.wallet.id,
                Transaction.receiver_id == current_user.wallet.id,
            ),
        )
        .group_by(Transaction.value_type)
    )
    response = await db.execute(
        query,
    )
    data_list = response.all()
    for data in data_list:
        obj = IncomeFromUser(
            type=data[0].value,
            value=data[1],
        )
        response_data.append(obj)

    return response_data


# ---------------------------------------------------------------------------
@router.get(path="/me", response_model=AgentRead)
async def me(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
) -> AgentRead:
    """
    ! Get My Agent Data

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User

    Returns
    -------
    obj
        Found agent

    Raises
    ------
    MerchantNotFoundException
    """
    obj = await agent_crud.find_by_user_id(db=db, user_id=current_user.id)
    return obj
