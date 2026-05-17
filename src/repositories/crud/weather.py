from typing import TYPE_CHECKING, Literal
import structlog
from sqlalchemy import and_, func, select, true, UnaryExpression
from src.exceptions import SortingFieldsNotProvided
from src.repositories.crud.models.weather import WeatherHistory
from src.schemas import WeatherCreate, WeatherRead
from src.schemas.pagination import (
    FilterSchema,
    PaginationResultSchema,
    PaginationSchema,
)

from .base import BaseRepository, IdType

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


class WeatherRepository(BaseRepository[WeatherHistory, WeatherRead, WeatherCreate]):
    model = WeatherHistory
    read_schema = WeatherRead
    create_schema = WeatherCreate

    def __init__(self, session: "AsyncSession") -> None:
        super().__init__(session)

    async def get_history_paginated(
        self,
        *,
        pagination: PaginationSchema,
        filter_schema: FilterSchema,
        user_id: IdType | None = None,  # type: ignore
        sort_by: str | None,
        order_by: Literal["asc", "desc"] | None,
    ) -> PaginationResultSchema[WeatherRead]:
        filters = self._build_filters(filter_schema=filter_schema, user_id=user_id)
        where_clause = and_(*filters) if filters else true()

        total_count: int = (
            await self.session.execute(
                select(func.count()).select_from(self.model).where(where_clause)
            )
        ).scalar_one()

        rows = (
            (
                await self.session.execute(
                    select(self.model)
                    .where(where_clause)
                    .order_by(
                        self._get_order_by_expr(
                            sort_by=sort_by,
                            order_by=order_by,
                        )
                    )
                    .offset(pagination.offset)
                    .limit(pagination.limit)
                )
            )
            .scalars()
            .all()
        )

        objects = [
            self.read_schema.model_validate(m, from_attributes=True) for m in rows
        ]

        return PaginationResultSchema(
            objects=objects,
            total_count=total_count,
            filtered_count=len(objects),
        )

    async def get_history_filtered(
        self,
        *,
        filter_schema: FilterSchema,
        user_id: IdType | None = None,  # type: ignore
        sort_by: str = "created_at",
        order_by: Literal["asc", "desc"] = "desc",
    ) -> list[WeatherRead]:
        filters = self._build_filters(filter_schema=filter_schema, user_id=user_id)

        rows = (
            (
                await self.session.execute(
                    select(self.model)
                    .where(and_(*filters) if filters else true())
                    .order_by(
                        self._get_order_by_expr(
                            sort_by=sort_by,
                            order_by=order_by,
                        )
                    )
                )
            )
            .scalars()
            .all()
        )

        return [self.read_schema.model_validate(m, from_attributes=True) for m in rows]

    def _build_filters(
        self,
        filter_schema: FilterSchema,
        user_id: IdType | None = None,  # type: ignore
    ) -> list:
        filters: list = []

        if user_id is not None:
            filters.append(self.model.user_id == user_id)
        if filter_schema.city_substring is not None:
            filters.append(
                self.model.city_name.ilike(f"%{filter_schema.city_substring}%")
            )
        if filter_schema.date_from is not None:
            filters.append(self.model.created_at >= filter_schema.date_from)
        if filter_schema.date_to is not None:
            filters.append(self.model.created_at <= filter_schema.date_to)

        return filters

    def _get_order_by_expr(
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
