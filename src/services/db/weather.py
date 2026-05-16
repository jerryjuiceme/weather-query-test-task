import uuid

from typing_extensions import Literal

from src.repositories.crud import WeatherRepository
from src.schemas.pagination import (
    FilterSchema,
    PaginationResultSchema,
    PaginationSchema,
)
from src.schemas.weather import WeatherRead, WeatherCreate


class WeatherService:
    def __init__(self, repository: WeatherRepository):
        self.repository = repository

    async def add_weather(self, *, weather_create: WeatherCreate) -> WeatherRead:
        return await self.repository.create(create_object=weather_create)

    async def get_history_paginated(
        self,
        *,
        pagination: PaginationSchema,
        user_id: uuid.UUID,
        filters: FilterSchema,
        sort_by: str | None,
        order_by: Literal["asc", "desc"] | None,
    ) -> PaginationResultSchema[WeatherRead]:

        return await self.repository.get_history_paginated(
            pagination=pagination,
            user_id=user_id,
            filters=filters,
            sort_by=sort_by,
            order_by=order_by,
        )

    async def get_history_filtered(
        self,
        *,
        user_id: uuid.UUID,
        filters: FilterSchema,
        sort_by: str = "created_at",
        order_by: Literal["asc", "desc"] = "desc",
    ) -> list[WeatherRead]:
        return await self.repository.get_history_filtered(
            user_id=user_id, filters=filters, sort_by=sort_by, order_by=order_by
        )
