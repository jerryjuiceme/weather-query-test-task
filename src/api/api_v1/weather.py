from typing import Literal

import structlog
from fastapi import APIRouter, Query
from waygate.fastapi import rate_limit
from src.services.http import WeatherHttpServiceDep
from src.api.dependencies.fastapi_users import CurrentUserDep
from src.schemas import WeatherRead, WeatherOutputMessage
from src.schemas import NotFoundError, RateLimitError
from src.config import settings

router = APIRouter(prefix="/weather", tags=["Weather"])

logger = structlog.get_logger()


@router.get(
    "",
    response_model=WeatherOutputMessage,
    status_code=200,
    responses={
        404: {
            "model": NotFoundError,
            "description": "City  not found",
        },
        429: {
            "model": RateLimitError,
            "description": "Rate limit exceeded",
        },
    },
    description="Get weather by city name, OpenWeatherMap API external service integration.",
)
@rate_limit(f"{settings.max_requests_per_minute}/minute")
async def get_weather(
    user: CurrentUserDep,
    service: WeatherHttpServiceDep,
    city: str = Query(..., min_length=2),
    units: Literal["metric", "imperial"] = Query("metric", enum=["metric", "imperial"]),
) -> WeatherRead:
    result = await service.fetch_weather(city=city, units=units, user_id=user.id)
    return result
