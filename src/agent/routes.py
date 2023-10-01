from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select

from src import deps
from src.ability.crud import ability as ability_crud
from src.agent.crud import agent as agent_crud
from src.agent.models import Agent
from src.agent.schema import (
    AgentFilter,
    AgentFilterOrderFild,
    AgentRead,
    AgentUpdate,
)
from src.schema import IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/agent", tags=["agent"])


# ---------------------------------------------------------------------------
@router.put(path="/update", response_model=AgentRead)
async def update_agent(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
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
    agent = await agent_crud.update_agents_interest_rates(
        db=db,
        target_agent=obj_current,
    )

    return agent


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=AgentRead)
async def find_agent(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
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
@router.get(path="/list", response_model=List[AgentRead])
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
        (Agent.is_main == filter_data.name) if filter_data.is_main else False
    )
    # * Add filter fields
    query = select(Agent).filter(
        or_(
            filter_data.return_all,
            filter_data.is_main,
        ),
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == AgentFilterOrderFild.is_main:
                query = query.order_by(Agent.is_main.desc())
            elif field == AgentFilterOrderFild.interest_rates:
                query = query.order_by(Agent.interest_rates.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == AgentFilterOrderFild.is_main:
                query = query.order_by(Agent.is_main.asc())
            elif field == AgentFilterOrderFild.interest_rates:
                query = query.order_by(Agent.interest_rates.asc())
    # * Find All agent with filters
    agent_list = await agent_crud.get_multi(db=db, skip=skip, limit=limit, query=query)

    return agent_list
