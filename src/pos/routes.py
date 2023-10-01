from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import deps
from src.merchant.crud import merchant as merchant_crud
from src.permission import permission_codes as permission
from src.pos.crud import pos as pos_crud
from src.pos.schema import PosBase, PosCreate, PosRead, PosUpdate
from src.schema import DeleteResponse, IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/pos", tags=["pos"])


# ---------------------------------------------------------------------------
@router.delete("/delete", response_model=DeleteResponse)
async def delete_pos(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.DELETE_POS]),
    ),
    delete_data: IDRequest,
) -> DeleteResponse:
    """
    ! Delete Pos

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    delete_data
        Necessary data for delete pos

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    PosNotFoundException
    """
    # * Verify pos existence
    await pos_crud.verify_existence(db=db, pos_id=delete_data.id)
    # * Delete Pos
    await pos_crud.delete(db=db, item_id=delete_data.id)

    return DeleteResponse(result="Pos Deleted Successfully")


# ---------------------------------------------------------------------------
@router.post("/create", response_model=PosBase)
async def create_pos(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CREATE_POS]),
    ),
    create_data: PosCreate,
) -> PosBase:
    """
    ! Create Pos

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    create_data
        Necessary data for create pos

    Returns
    -------
    pos
        New pos

    Raises
    ------
    PosTokenIsDuplicatedException
    MerchantNotFoundException
    """
    # * Verify merchant existence
    await merchant_crud.verify_existence(db=db, merchant_id=create_data.merchant_id)
    # * Verify pos Token duplicated
    await pos_crud.verify_duplicate_token(db=db, token=create_data.token)
    # * Create Pos
    pos = await pos_crud.create(db=db, obj_in=create_data)

    return pos


# ---------------------------------------------------------------------------
@router.put("/update", response_model=PosRead)
async def update_pos(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_POS]),
    ),
    update_data: PosUpdate,
) -> PosRead:
    """
    ! Update Pos

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update pos

    Returns
    -------
    pos
        Updated pos

    Raises
    ------
    PosNotFoundException
    PosTokenIsDuplicatedException
    MerchantNotFoundException
    """
    # * Verify merchant existence
    await merchant_crud.verify_existence(
        db=db,
        merchant_id=update_data.data.merchant_id,
    )
    # * Verify pos existence
    obj_current = await pos_crud.verify_existence(db=db, pos_id=update_data.where.id)
    # * Verify pos token duplicate
    await pos_crud.verify_duplicate_token(db=db, token=update_data.data.token)
    # * Update pos
    pos = await pos_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )

    return pos


# ---------------------------------------------------------------------------
@router.get("/list", response_model=list[PosRead])
async def read_pos_list(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_POS]),
    ),
    skip: int = 0,
    limit: int = 10,
) -> list[PosRead]:
    """
    ! Read Pos

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
    pos_list
        List of pos
    """
    pos_list = await pos_crud.get_multi(db=db, skip=skip, limit=limit)
    return pos_list


# ---------------------------------------------------------------------------
@router.post("/find", response_model=PosRead)
async def find_pos(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_POS]),
    ),
    read_data: IDRequest,
) -> PosRead:
    """
    ! Find Pos

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    read_data
        Target Pos's ID

    Returns
    -------
    pos
        Found Pos

    Raises
    ------
    PosNotFoundException
    """
    # * Verify pos existence
    pos = await pos_crud.verify_existence(db=db, pos_id=read_data.id)
    return pos
