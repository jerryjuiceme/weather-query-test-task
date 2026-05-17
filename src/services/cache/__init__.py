__all__ = ["get_cache_service", "WeatherCacheDep", "WeatherCacheService"]

from typing import Annotated

from fastapi import Depends

from .weather import WeatherCacheService
from src.repositories.cache import CacheRepositoryProtocol, get_cache_repository

###########################
## SERVICES DEPENDENCIES ##
###########################


def get_cache_service(
    cache_repository: Annotated[
        "CacheRepositoryProtocol",
        Depends(get_cache_repository),
    ],
) -> WeatherCacheService:
    return WeatherCacheService(cache_repository)


WeatherCacheDep = Annotated[WeatherCacheService, Depends(get_cache_service)]
