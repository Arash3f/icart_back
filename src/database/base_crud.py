import uuid
from typing import Any, Generic, Sequence, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select

from src.database.base_class import Base

# ---------------------------------------------------------------------------
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


# ---------------------------------------------------------------------------
class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    ? Base ORM Utils that use in all models
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, *, db: AsyncSession, item_id: uuid.UUID) -> ModelType:
        """
        ? Get Item With ID

        Parameters
        ----------
        db
            Target database connection
        item_id
            Target Item ID

        Returns
        -------
        obj
            Found item
        """
        response = await db.execute(select(self.model).where(self.model.id == item_id))
        return response.scalar_one_or_none()

    async def get_by_ids(
        self,
        *,
        db: AsyncSession,
        list_ids: list[uuid.UUID],
    ) -> Sequence[ModelType] | None:
        """
        ? Get Multiple Item With ID List

        Parameters
        ----------
        db
            Target database connection
        list_ids
            Target id list

        Returns
        -------
        obj_list
            Found items
        """
        response = await db.execute(
            select(self.model).where(self.model.id.in_(list_ids)),
        )
        obj_list = response.scalars().all()

        return obj_list

    async def get_multi(
        self,
        *,
        db: AsyncSession,
        query: Select | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[ModelType] | None:
        """
        ? Get Multiple Item With Filter

        Parameters
        ----------
        db
            Target database connection
        query
            Customize query for filter
        skip
            Skip some item from list
        limit
            Limit of item's count

        Returns
        -------
        obj_list
            Found items
        """
        if query is None:
            query = select(self.model).offset(skip).limit(limit)
        response = await db.execute(query)
        obj_list = response.scalars().all()

        return obj_list

    async def create(self, *, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """
        ? Creat New Object

        Parameters
        ----------
        db
            Target database connection
        obj_in
            Target data for create

        Returns
        -------
        new_obj
            Created object
        """
        obj_in_data = jsonable_encoder(obj_in)
        new_obj = self.model(**obj_in_data)
        db.add(new_obj)
        await db.commit()
        await db.refresh(new_obj)
        return new_obj

    async def create_multi(
        self,
        *,
        db: AsyncSession,
        objs_in: list[dict[str, Any]],
    ) -> bool:
        """
        ? Creat Multiple Objects

        Parameters
        ----------
        db
            Target database connection
        objs_in
            Target data for create

        Returns
        -------
        result
            Result of operation
        """
        await db.run_sync(
            lambda session: session.bulk_insert_mappings(
                mapper=self.model,
                mappings=objs_in,
            ),
        )
        return True

    async def update(
        self,
        *,
        db: AsyncSession,
        obj_current: ModelType,
        obj_new: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """
        ? Update Object

        Parameters
        ----------
        db
            Target database connection
        obj_current
            Current data
        obj_new
            New data

        Returns
        -------
        updated_obj
            Updated object

        """
        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.model_dump(exclude_unset=False)
        for field in update_data:
            setattr(obj_current, field, update_data[field])
        db.add(obj_current)
        await db.commit()
        await db.refresh(obj_current)
        return obj_current

    async def delete(self, *, db: AsyncSession, item_id: uuid.UUID) -> bool:
        """
        ! Delete Object

        Parameters
        ----------
        db
            Target database connection
        item_id
            Target item id

        Returns
        -------
        result
            Result of operation
        """
        obj = await db.get(entity=self.model, ident=item_id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return True
