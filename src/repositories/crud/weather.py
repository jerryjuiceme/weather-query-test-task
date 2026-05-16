from typing import TYPE_CHECKING, Literal

from sqlalchemy import and_, func, select, true

from src.repositories.crud.models.weather import WeatherHistory
from src.schemas.pagination import (
    FilterSchema,
    PaginationResultSchema,
    PaginationSchema,
)
from src.schemas.weather import WeatherCreate, WeatherRead

from .base import BaseRepository, IdType

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class WeatherRepository(BaseRepository[WeatherHistory, WeatherRead, WeatherCreate]):
    model = WeatherHistory
    read_schema = WeatherRead
    create_schema = WeatherCreate

    def __init__(self, session: "AsyncSession") -> None:
        super().__init__(session)

    def _build_filters(
        self,
        *,
        filters: FilterSchema,
        user_id: IdType | None = None,  # type: ignore
    ) -> list:
        clauses: list = []

        if user_id is not None:
            clauses.append(self.model.user_id == user_id)
        if filters.city_substring is not None:
            clauses.append(self.model.city_name.ilike(f"%{filters.city_substring}%"))
        if filters.date_from is not None:
            clauses.append(self.model.created_at >= filters.date_from)
        if filters.date_to is not None:
            clauses.append(self.model.created_at <= filters.date_to)

        return clauses

    async def get_history_paginated(
        self,
        *,
        pagination: PaginationSchema,
        filters: FilterSchema,
        user_id: IdType | None = None,  # type: ignore
        sort_by: str | None,
        order_by: Literal["asc", "desc"] | None,
    ) -> PaginationResultSchema[WeatherRead]:
        clauses = self._build_filters(filters=filters, user_id=user_id)
        where_clause = and_(*clauses) if clauses else true()

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
                        self.get_order_by_expr(sort_by=sort_by, order_by=order_by)
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
        filters: FilterSchema,
        *,
        user_id: IdType | None = None,  # type: ignore
        sort_by: str = "created_at",
        order_by: Literal["asc", "desc"] = "desc",
    ) -> list[WeatherRead]:
        clauses = self._build_filters(filters=filters, user_id=user_id)

        rows = (
            (
                await self.session.execute(
                    select(self.model)
                    .where(and_(*clauses) if clauses else true())
                    .order_by(
                        self.get_order_by_expr(sort_by=sort_by, order_by=order_by)
                    )
                )
            )
            .scalars()
            .all()
        )

        return [self.read_schema.model_validate(m, from_attributes=True) for m in rows]
