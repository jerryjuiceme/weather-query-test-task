from typing import Literal

import structlog
from fastapi import APIRouter, Query
from waygate.fastapi import rate_limit
from src.services.http import WeatherHttpServiceDep
from src.api.dependencies.fastapi_users import CurrentUserDep
from src.schemas import WeatherRead, WeatherOutputMessage

router = APIRouter(prefix="/weather", tags=["Weather"])

logger = structlog.get_logger()


@router.get("", response_model=WeatherOutputMessage)
@rate_limit("30/minute")
async def get_weather(
    user: CurrentUserDep,
    service: WeatherHttpServiceDep,
    city: str = Query(..., min_length=2),
    units: Literal["metric", "imperial"] = Query("metric", enum=["metric", "imperial"]),
) -> WeatherRead:
    result = await service.fetch_weather(city=city, units=units, user_id=user.id)
    return result
