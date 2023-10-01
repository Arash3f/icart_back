from fastapi import APIRouter, Depends

from src import deps
from src.user.models import User
from src.user.schema import UserReadWithRole

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/user", tags=["user"])


# ---------------------------------------------------------------------------
@router.get("/me", response_model=UserReadWithRole)
async def current_user(current_user: User = Depends(deps.get_current_user())) -> User:
    """
    ! Get My data

    Parameters
    ----------
    current_user
        Requester User

    Returns
    -------
    user
        Requester User data

    """
    user = current_user
    return user
