import structlog


from fastapi import APIRouter, Query
from waygate.fastapi import rate_limit

router = APIRouter(prefix="/weather", tags=["Weather"])

logger = structlog.get_logger()


@router.get("")
@rate_limit("30/minute")
async def get_weather(
    # user: CurrentUserDep,
    city: str = Query(..., min_length=2),
    units: str = Query("metric", enum=["metric", "imperial"]),
    # service: WeatherService = Depends(get_weather_service),
):
    return {
        "city": city,
        "units": units,
        # "user_id": user.id,
    }
