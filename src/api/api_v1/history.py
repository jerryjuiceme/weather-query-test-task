import datetime as dt
from src.utils.csv import parse_to_csv
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from src.api.dependencies.fastapi_users import CurrentUserDep
from src.schemas.pagination import (
    FilterSchema,
    PaginationRequestSchema,
    PaginationResultSchema,
)
from src.schemas import WeatherOutputMessage, WeatherRead
from src.services.db import WeatherServiceDep
from src.schemas import ErrorResponse, NotFoundError

router = APIRouter(prefix="/history", tags=["History"])

logger = structlog.get_logger()


@router.get(
    "",
    response_model=PaginationResultSchema[WeatherOutputMessage],
    status_code=200,
    responses={400: {"model": ErrorResponse, "description": "Bad request"}},
    description="Get weather history per user. If a superuser then can get all history",
)
async def get_history(
    user: CurrentUserDep,
    service: WeatherServiceDep,
    pagination_request: PaginationRequestSchema = Depends(),
    city: str = Query(None, min_length=2),
    date_from: dt.datetime = Query(None),
    date_to: dt.datetime = Query(None),
) -> PaginationResultSchema[WeatherRead]:

    # if user is superuser then can get all history
    if user.is_superuser:
        user_id = user.id
    else:
        user_id = None
    return await service.get_history_paginated(
        pagination=pagination_request.to_pagination_schema(),
        user_id=user_id,
        filter_schema=FilterSchema(
            city_substring=city, date_from=date_from, date_to=date_to
        ),
        sort_by=pagination_request.sort,
        order_by=pagination_request.order_by,
    )


@router.get(
    "/export",
    response_class=StreamingResponse,
    status_code=200,
    responses={
        404: {"description": "No data to export", "model": NotFoundError},
        400: {"description": "Bad request", "model": ErrorResponse},
    },
    description="Export weather history per user. If a superuser then can get all history",
)
async def export_history(
    user: CurrentUserDep,
    service: WeatherServiceDep,
    city: str = Query(None, min_length=2),
    date_from: dt.datetime = Query(None),
    date_to: dt.datetime = Query(None),
) -> StreamingResponse:
    logger.info(
        "Export history", city=city, date_from=date_from, date_to=date_to, user=user
    )
    # will check if user is superuser then can get all history
    if user.is_superuser:
        user_id = user.id
    else:
        user_id = None

    items = await service.get_history_filtered(
        user_id=user_id,
        filter_schema=FilterSchema(
            city_substring=city,
            date_from=date_from,
            date_to=date_to,
        ),
    )
    if not items:
        raise HTTPException(status_code=404, detail="No data to export")
    file_iter = parse_to_csv(items)

    filename = f"export_{dt.datetime.now(tz=dt.timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    return StreamingResponse(
        file_iter,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
