import uuid
from typing import Literal
from time import perf_counter
import structlog
from src.schemas import WeatherCreate, WeatherData, WeatherRead

from src.repositories.http import HttpRepository
from src.services.cache.weather import WeatherCacheService
from src.services.db import WeatherService

logger = structlog.get_logger()


class WeatherHttpService:
    def __init__(
        self,
        http_repository: HttpRepository,
        cache_service: WeatherCacheService,
        crud: WeatherService,
    ):
        self.http = http_repository
        self.cache = cache_service
        self.crud = crud

    async def fetch_weather(
        self,
        *,
        city: str,
        units: Literal["metric", "imperial"] = "metric",
        user_id: uuid.UUID,
    ) -> WeatherRead:

        logger.info(
            "Fetching weather from OpenWeatherMap",
            city=city,
            units=units,
        )

        # --------- Cached ---------
        self.cache.set_key("weather", city, units)
        cached_result = await self.cache.get()
        if cached_result:
            weather: WeatherCreate = WeatherCreate(
                user_id=user_id,
                is_from_cache=True,
                **cached_result.model_dump(),
            )
            weather_resp = await self.crud.add_weather(weather_create=weather)
            logger.info(
                "Weather fetched from cache",
                user=user_id,
                city=city,
                units=units,
            )
            weather_resp.is_from_cache = True
            return weather_resp

        # --------- Not cached ---------
        start_time = perf_counter()
        weather_resp: WeatherData = await self.http.get_weather_by_city(
            city=city, units=units
        )
        request_time = perf_counter() - start_time
        weather: WeatherCreate = WeatherCreate(
            user_id=user_id,
            **weather_resp.model_dump(),
        )
        weather_resp = await self.crud.add_weather(weather_create=weather)
        await self.cache.set(value=weather, expire=5 * 60)

        logger.info(
            "Weather fetched from OpenWeatherMap",
            user=user_id,
            city=city,
            units=units,
            time=request_time,
        )
        return weather_resp
