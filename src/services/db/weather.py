import uuid
import structlog
from typing_extensions import Literal

from src.repositories.crud import WeatherRepository
from src.schemas.pagination import (
    FilterSchema,
    PaginationResultSchema,
    PaginationSchema,
)
from src.schemas import WeatherRead, WeatherCreate
from src.schemas.weather import WeatherOutputMessage

logger = structlog.get_logger()


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
        filter_schema: FilterSchema,
        sort_by: str | None,
        order_by: Literal["asc", "desc"] | None,
    ) -> PaginationResultSchema[WeatherRead]:
        logger.info(
            "Get history", user_id=user_id, pagination=pagination, filter=filter_schema
        )
        return await self.repository.get_history_paginated(
            pagination=pagination,
            user_id=user_id,
            filter_schema=filter_schema,
            sort_by=sort_by,
            order_by=order_by,
        )

    async def get_history_filtered(
        self,
        *,
        user_id: uuid.UUID,
        filter_schema: FilterSchema,
        sort_by: str = "created_at",
        order_by: Literal["asc", "desc"] = "desc",
    ) -> list[WeatherOutputMessage]:
        return await self.repository.get_history_filtered(
            user_id=user_id,
            filter_schema=filter_schema,
            sort_by=sort_by,
            order_by=order_by,
        )
