__all__ = ["WeatherHttpService", "WeatherHttpServiceDep", "get_weather_service"]

from typing import Annotated, TYPE_CHECKING

from src.repositories.crud.db import get_db_request
from src.services.cache import WeatherCacheService, get_cache_service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends

from .weather import WeatherHttpService
from src.repositories.http import HttpRepository, get_weather_repo
from src.repositories.crud import WeatherRepository
from src.services.db import WeatherService

###########################
## SERVICES DEPENDENCIES ##
###########################


def get_weather_service(
    session: Annotated["AsyncSession", Depends(get_db_request)],
    cache_service: Annotated["WeatherCacheService", Depends(get_cache_service)],
    http_repository: Annotated["HttpRepository", Depends(get_weather_repo)],
) -> WeatherHttpService:
    crud_service = WeatherService(repository=WeatherRepository(session=session))
    return WeatherHttpService(
        http_repository=http_repository,
        cache_service=cache_service,
        crud=crud_service,
    )


WeatherHttpServiceDep = Annotated[WeatherHttpService, Depends(get_weather_service)]
