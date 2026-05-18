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
            "Get history request received",
            pagination=pagination,
            city=filter_schema.city_substring,
            date_from=filter_schema.date_from,
            date_to=filter_schema.date_to,
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
        logger.info(
            "Get history export request received",
            city=filter_schema.city_substring,
            date_from=filter_schema.date_from,
            date_to=filter_schema.date_to,
        )
        return await self.repository.get_history_filtered(
            user_id=user_id,
            filter_schema=filter_schema,
            sort_by=sort_by,
            order_by=order_by,
        )
