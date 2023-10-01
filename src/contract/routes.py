from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select

from src import deps
from src.contract.crud import contract as contract_crud
from src.contract.models import Contract
from src.contract.schema import ContractRead
from src.schema import IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/contract", tags=["contract"])


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=ContractRead)
async def find_contract(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    obj_data: IDRequest,
) -> ContractRead:
    """
    ! Find Contract

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
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

    return obj


# ---------------------------------------------------------------------------
@router.get(path="/list", response_model=List[ContractRead])
async def get_contract(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    skip: int = 0,
    limit: int = 20,
) -> List[ContractRead]:
    """
    ! Get All Contract

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    skip
        Pagination skip
    limit
        Pagination limit

    Returns
    -------
    obj_list
        List of ability
    """
    obj_list = await contract_crud.get_multi(db=db, skip=skip, limit=limit)
    return obj_list


# ---------------------------------------------------------------------------
@router.get(path="/list/my", response_model=List[ContractRead])
async def get_my_contract_list(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user()),
    skip: int = 0,
    limit: int = 20,
) -> List[ContractRead]:
    """
    ! Get All My Contract

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    skip
        Pagination skip
    limit
        Pagination limit

    Returns
    -------
    obj_list
        List of ability

    """
    query = select(Contract).where(
        Contract.position_request.requester_user_id == current_user.id,
    )
    obj_list = await contract_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return obj_list
