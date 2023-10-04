from typing import List

from fastapi import APIRouter, Depends

from src import deps
from src.crypto.crud import crypto as crypto_crud
from src.crypto.schema import CryptoCreate, CryptoRead, CryptoUpdate
from src.permission import permission_codes as permission
from src.schema import DeleteResponse, IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/crypto", tags=["crypto"])


# ---------------------------------------------------------------------------
@router.delete(path="/delete", response_model=DeleteResponse)
async def delete_crypto(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.DELETE_CRYPTO]),
    ),
    delete_data: IDRequest,
) -> DeleteResponse:
    """
    ! Delete Crypto

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    delete_data
        Necessary data for delete crypto

    Returns
    -------
    obj
        Result of operation

    Raises
    ------
    CryptoNotFoundException
    """
    # * Verify crypto existence
    await crypto_crud.verify_existence(db=db, crypto_id=delete_data.id)
    # * Delete crypto
    await crypto_crud.delete(db=db, item_id=delete_data.id)
    return DeleteResponse(result="Crypto Deleted Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/create", response_model=CryptoRead)
async def create_crypto(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CREATE_CRYPTO]),
    ),
    create_data: CryptoCreate,
) -> CryptoRead:
    """
    ! Create Crypto

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    create_data
        Necessary data for create crypto

    Returns
    -------
    obj
        New crypto

    Raises
    ------
    CryptoNameIsDuplicatedException
    """
    # * Verify crypto name duplicate
    await crypto_crud.verify_duplicate_name(db=db, name=create_data.name)
    # * Create crypto
    obj = await crypto_crud.create(db=db, obj_in=create_data)
    return obj


# ---------------------------------------------------------------------------
@router.put(path="/update", response_model=CryptoRead)
async def update_crypto(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_CRYPTO]),
    ),
    update_data: CryptoUpdate,
) -> CryptoRead:
    """

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    update_data
        Necessary data for update crypto

    Returns
    -------
    ovj
        Updated crypto

    Raises
    ------
    CryptoNotFoundException
    CryptoNameIsDuplicatedException
    """
    # * Verify crypto existence
    obj_current = await crypto_crud.verify_existence(
        db=db,
        crypto_id=update_data.where.id,
    )
    # * Verify crypto name duplicate
    await crypto_crud.verify_duplicate_name(
        db=db,
        name=update_data.data.name,
        exception_name=obj_current.name,
    )

    obj = await crypto_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )
    return obj


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=CryptoRead)
async def get_crypto(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_CRYPTO]),
    ),
    obj_data: IDRequest,
) -> CryptoRead:
    """
    ! Find Crypto

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    obj_data
        Target Crypto's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    CryptoNotFoundException
    """
    # * Verify crypto existence
    obj = await crypto_crud.verify_existence(db=db, crypto_id=obj_data.id)
    return obj


# ---------------------------------------------------------------------------
@router.post(path="/list", response_model=List[CryptoRead])
async def get_crypto_list(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_CRYPTO]),
    ),
    skip: int = 0,
    limit: int = 20,
) -> List[CryptoRead]:
    """
    ! Get All Crypto

    Parameters
    ----------
    db
        Target database connection
    current_user
        Requester User
    skip
        Pagination skip
    limit
        agination limit

    Returns
    -------
    obj_list
        list of crypto
    """
    obj_list = await crypto_crud.get_multi(db=db, skip=skip, limit=limit)
    return obj_list
