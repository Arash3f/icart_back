from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select

from src import deps
from src.contract.crud import contract as contract_crud
from src.contract.models import Contract
from src.contract.schema import ContractRead
from src.schema import IDRequest, VerifyUserDep
from src.user.models import User
from src.permission import permission_codes as permission

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
    verify_data: VerifyUserDep = Depends(
        deps.is_user_have_permission([permission.VIEW_CONTRACT]),
    ),
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

    Returns
    -------
    obj_list
        List of ability
    """
    query = select(Contract)
    # * Not Have permissions
    if not verify_data.is_valid:
        query = query.where(
            Contract.position_request.requester_user_id == verify_data.user.id,
        )
    obj_list = await contract_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return obj_list
