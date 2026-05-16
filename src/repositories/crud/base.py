import structlog
import uuid
from typing import TYPE_CHECKING, Generic, TypeVar

from sqlalchemy import Delete, UnaryExpression, select

from src.exceptions import SortingFieldsNotProvided
from src.repositories.crud.db import ModelBase as BaseModelSQL
from src.schemas.base import BaseModel, CreateBaseModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

IdType = TypeVar("IdType", bound=int | uuid.UUID)
ReadSchemaT = TypeVar("ReadSchemaT", bound=BaseModel)
CreateSchemaT = TypeVar("CreateSchemaT", bound=CreateBaseModel)
ModelBaseType = TypeVar("ModelBaseType", bound=BaseModelSQL)


logger = structlog.get_logger()


class BaseRepository(Generic[ModelBaseType, ReadSchemaT, CreateSchemaT]):
    model: type[ModelBaseType] = None  # type: ignore
    read_schema: type[ReadSchemaT]
    create_schema: type[CreateSchemaT]

    def __init__(self, session: "AsyncSession") -> None:
        """
        Base CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `read_schema`: A Pydantic model (schema) class
        * `create_schema`: A Pydantic model (schema) class
        """
        self.session = session
        if self.model is None:
            raise ValueError("The model is not defined")

    async def get_all(self, **kwargs) -> list[ReadSchemaT] | None:
        """
        Get all models.
        """
        stmt = select(self.model.__table__.columns).filter_by(**kwargs)  # type: ignore
        result = await self.session.execute(stmt)
        return [
            self.read_schema.model_validate(m, from_attributes=True)
            for m in result.mappings().all()
        ]

    async def get_one_or_none(self, id: IdType) -> ReadSchemaT | None:  # type: ignore
        """
        Get a model or None by identifier.
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        result = result.scalar_one_or_none()
        if result is None:
            return None
        return self.read_schema.model_validate(result, from_attributes=True)

    async def create(self, create_object: CreateSchemaT) -> ReadSchemaT:
        """
        Create a model.
        """
        model = self.model(**create_object.model_dump())
        self.session.add(model)
        await self.session.flush()
        # await self.session.commit()
        return self.read_schema.model_validate(model, from_attributes=True)

    async def delete(self, id: IdType) -> None:  # type: ignore
        """
        Delete models.
        """
        stmt = Delete(self.model).where(self.model.id == id)
        await self.session.execute(stmt)
        # await self.session.commit()

    def get_order_by_expr(
        self, sort_by: str | None, order_by: str | None
    ) -> UnaryExpression:
        try:
            sort_by = sort_by or "id"
            order_by = order_by or "asc"
            if order_by == "asc":
                order_by_expr = getattr(self.model, sort_by).asc()
            else:
                order_by_expr = getattr(self.model, sort_by).desc()
        except AttributeError as attribute_error:
            logger.warning(
                "Could not find field for sorting: %s. Details: %s",
                sort_by,
                attribute_error,
            )
            raise SortingFieldsNotProvided(
                detail=f"Could not find field for sorting: {sort_by}.",
            )

        return order_by_expr
