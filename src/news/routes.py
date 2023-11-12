from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_

from src import deps
from src.log.models import LogType
from src.news.crud import news as news_crud
from src.log.crud import log as log_crud
from src.news.models import News
from src.news.schema import (
    NewsCreate,
    NewsRead,
    NewsShortRead,
    NewsUpdate,
    NewsFilter,
    NewsFilterOrderFild,
)
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
    news = await news_crud.verify_existence(db=db, news_id=delete_data.id)
    await news_crud.delete(db=db, item_id=delete_data.id)

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.DELETE_NEWS,
        detail="اعلان با عنوان ( {} ) با موفقیت توسط کاربر {} حذف شد".format(
            news.title,
            current_user.username,
        ),
    )

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

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.CREATE_NEWS,
        detail="اعلان با عنوان ( {} ) با موفقیت توسط کاربر {} ایحاد شد".format(
            obj.title,
            current_user.username,
        ),
    )

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

    # ? Generate Log
    await log_crud.auto_generate(
        db=db,
        user_id=current_user.id,
        log_type=LogType.UPDATE_NEWS,
        detail="اعلان با عنوان ( {} ) با موفقیت توسط کاربر {} ویرایش شد".format(
            obj.title,
            current_user.username,
        ),
    )

    return obj


# ---------------------------------------------------------------------------
@router.post(path="/find", response_model=NewsRead)
async def find_news(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user(),
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
@router.post(path="/list", response_model=List[NewsShortRead])
async def get_news_list(
    *,
    db=Depends(deps.get_db),
    current_user: User = Depends(
        deps.get_current_user(),
    ),
    filter_data: NewsFilter,
    skip: int = 0,
    limit: int = 20,
) -> List[NewsShortRead]:
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
        (News.title.contains(filter_data.title)) if filter_data.title else True
    )
    # * Add filter fields
    query = select(News).filter(
        and_(
            filter_data.title,
        ),
    )
    # * Prepare order fields
    if filter_data.order_by:
        for field in filter_data.order_by.desc:
            # * Add filter fields
            if field == NewsFilterOrderFild.title:
                query = query.order_by(News.title.desc())
        for field in filter_data.order_by.asc:
            # * Add filter fields
            if field == NewsFilterOrderFild.title:
                query = query.order_by(News.title.asc())
    obj_list = await news_crud.get_multi(db=db, skip=skip, limit=limit, query=query)
    return obj_list
