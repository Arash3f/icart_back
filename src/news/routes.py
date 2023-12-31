from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select

from src import deps
from src.news.crud import news as news_crud
from src.news.models import News
from src.news.schema import NewsCreate, NewsFilter, NewsRead, NewsUpdate
from src.permission import permission_codes as permission
from src.schema import DeleteResponse, IDRequest
from src.user.models import User

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/news", tags=["news"])


# ---------------------------------------------------------------------------
@router.delete(path="/delete", response_model=DeleteResponse)
async def delete_news(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.DELETE_NEWS]),
    ),
    delete_data: IDRequest,
) -> DeleteResponse:
    """
    ! Delete News

    Parameters
    ----------
    db
        Target database connection
    current_user
        Required permissions
    delete_data
        Necessary data for delete news

    Returns
    -------
    response
        Result of operation

    Raises
    ------
    NewsNotFoundException
    """
    # * Verify news existence
    await news_crud.verify_existence(db=db, news_id=delete_data.id)
    await news_crud.delete(db=db, item_id=delete_data.id)
    return DeleteResponse(result="News Deleted Successfully")


# ---------------------------------------------------------------------------
@router.post(path="/create", response_model=NewsRead)
async def create_news(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.CREATE_NEWS]),
    ),
    create_data: NewsCreate,
) -> NewsRead:
    """
    ! Create News

    Parameters
    ----------
    db
        Target database connection
    current_user
        Required permissions
    create_data
        Necessary data for create news

    Returns
    -------
    obj
        New news
    """
    obj = await news_crud.create(db=db, obj_in=create_data)
    return obj


# ---------------------------------------------------------------------------
@router.put(path="/update", response_model=NewsRead)
async def update_news(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.UPDATE_NEWS]),
    ),
    update_data: NewsUpdate,
) -> NewsRead:
    """
    ! Update News

    Parameters
    ----------
    db
        Target database connection
    current_user
        Required permissions
    update_data
        Necessary data for update news

    Returns
    -------
    obj
        Updated news

    Raises
    ------
    NewsNotFoundException
    """
    # * Verify news existence
    obj_current = await news_crud.verify_existence(db=db, news_id=update_data.where.id)

    obj = await news_crud.update(
        db=db,
        obj_current=obj_current,
        obj_new=update_data.data,
    )
    return obj


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=NewsRead)
async def find_news(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_NEWS]),
    ),
    obj_data: IDRequest,
) -> NewsRead:
    """
    ! Find News

    Parameters
    ----------
    db
        Target database connection
    current_user
        Required permissions
    obj_data
        Target News's ID

    Returns
    -------
    obj
        Found Item

    Raises
    ------
    NewsNotFoundException
    """
    # * Verify news existence
    obj = await news_crud.verify_existence(db=db, news_id=obj_data.id)

    return obj


# ---------------------------------------------------------------------------
@router.get(path="/list", response_model=List[NewsRead])
async def get_news_list(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user_with_permissions([permission.VIEW_NEWS]),
    ),
    filter_data: NewsFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[NewsRead]:
    """
    ! Get All News

    Parameters
    ----------
    db
        Target database connection
    current_user
        Required permissions
    skip
        Pagination skip
    limit
        Pagination limit
    filter_data
        Filter data

    Returns
    -------
    obj_list
        List of ability
    """
    # * Prepare filter fields
    filter_data.title = (
        (News.title.contain(filter_data.title)) if filter_data.title else False
    )
    # * Add filter fields
    query = select(News).filter(
        or_(
            filter_data.return_all,
            filter_data.title,
        ),
    )
    # * Find All agent with filters
    obj_list = await news_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return obj_list
