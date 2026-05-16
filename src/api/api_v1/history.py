from datetime import datetime

import structlog
from typing import Annotated, Any, Literal
from uuid import UUID
from waygate.fastapi import rate_limit
from fastapi import APIRouter, Depends, Form, Query, status

from src.api.dependencies.fastapi_users import CurrentUserDep
from src.schemas.pagination import (
    PaginationRequestSchema,
    PaginationSchema,
    FilterSchema,
    PaginationResultSchema,
)
from src.schemas.weather import WeatherOutputMessage, WeatherRead
from src.services.db import WeatherServiceDep

router = APIRouter(prefix="/history", tags=["history"])

logger = structlog.get_logger()


@router.get("/", response_model=PaginationResultSchema[WeatherOutputMessage])
@rate_limit("5/minute")
async def get_history(
    user: CurrentUserDep,
    service: WeatherServiceDep,
    pagination_request: PaginationRequestSchema = Depends(),
    city: str = Query(..., min_length=2),
    date_from: datetime = Query(None),
    date_to: datetime = Query(None),
) -> PaginationResultSchema[WeatherRead]:

    return await service.get_history_paginated(
        pagination=pagination_request.to_pagination_schema(),
        user_id=user.id,
        filters=FilterSchema(city_substring=city, date_from=date_from, date_to=date_to),
        sort_by=pagination_request.sort,
        order_by=pagination_request.order_by,
    )
    # return await service.get_history_paginated(pagination=pagination, filters=filters)


@router.get("/export")
async def export_history(
    filters: FilterSchema,
    user: CurrentUserDep,
    service: WeatherServiceDep,
) -> Any:
    return {}
    ...
    # return await service.get_history_filtered(pagination=pagination, filters=filters)
