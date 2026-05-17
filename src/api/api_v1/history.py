from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Query
from waygate.fastapi import rate_limit

from src.api.dependencies.fastapi_users import CurrentUserDep
from src.schemas.pagination import (
    FilterSchema,
    PaginationRequestSchema,
    PaginationResultSchema,
)
from src.schemas import WeatherOutputMessage, WeatherRead
from src.services.db import WeatherServiceDep

router = APIRouter(prefix="/history", tags=["History"])

logger = structlog.get_logger()


@router.get("/", response_model=PaginationResultSchema[WeatherOutputMessage])
@rate_limit("5/minute")
async def get_history(
    user: CurrentUserDep,
    service: WeatherServiceDep,
    pagination_request: PaginationRequestSchema = Depends(),
    city: str = Query(None, min_length=2),
    date_from: datetime = Query(None),
    date_to: datetime = Query(None),
) -> PaginationResultSchema[WeatherRead]:

    return await service.get_history_paginated(
        pagination=pagination_request.to_pagination_schema(),
        user_id=user.id,
        filter_schema=FilterSchema(
            city_substring=city, date_from=date_from, date_to=date_to
        ),
        sort_by=pagination_request.sort,
        order_by=pagination_request.order_by,
    )
    # return await service.get_history_paginated(pagination=pagination, filters=filters)


@router.get("/export")
async def export_history(
    user: CurrentUserDep,
    service: WeatherServiceDep,
    city: str = Query(None, min_length=2),
    date_from: datetime = Query(None),
    date_to: datetime = Query(None),
) -> Any:
    if user.is_superuser:
        user_id = None
    return {}
    ...
    # return await service.get_history_filtered(pagination=pagination, filters=filters)
