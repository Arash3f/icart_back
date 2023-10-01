from typing import List

from fastapi import APIRouter, Depends

from src import deps
from src.important_data.crud import important_data as important_data_crud
from src.important_data.schema import ImportantDataRead, ImportantDataUpdate
from src.permission import permission_codes as permission
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/important_data", tags=["important_data"])


# ---------------------------------------------------------------------------
@router.put(path="/update", response_model=ImportantDataRead)
async def update_important_data(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_IMPORTANT_DATA]),
    ),
    update_data: ImportantDataUpdate,
) -> ImportantDataRead:
    """
    ! Update ImportantData

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
         Necessary data for update important_data

    Returns
    -------
    obj
        Updated important_data

    Raises
    ------
    ImportantDataNotFoundException
    """
    # * Verify important_data existence
    obj_current = await important_data_crud.verify_existence(
        db=db,
        user_crypto_id=update_data.where.id,
    )
    # * Update
    obj = await important_data_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )
    return obj


# ---------------------------------------------------------------------------
@router.get(path="/list", response_model=List[ImportantDataRead])
async def get_important_data_list(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_IMPORTANT_DATA]),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[ImportantDataRead]:
    """
    ! Get All Important Data

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
        All Important Data
    """
    obj_list = await important_data_crud.get_multi(db=db, skip=skip, limit=limit)
    return obj_list
