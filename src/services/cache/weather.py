from typing_extensions import Annotated
from fastapi import Depends
from src.repositories.cache import CacheRepositoryProtocol, get_cache_repository
from src.schemas import WeatherRead

from .base import BaseCacheService
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.cache import CacheRepositoryProtocol


class WeatherCacheService(BaseCacheService[WeatherRead]):
    read_schema = WeatherRead

    def __init__(self, cache_repository: "CacheRepositoryProtocol") -> None:
        super().__init__(cache_repository)


def get_note_service(
    cache_repository: Annotated[
        "CacheRepositoryProtocol", Depends(get_cache_repository)
    ],
) -> WeatherCacheService:
    return WeatherCacheService(cache_repository)


WeatherCacheDep = Annotated[WeatherCacheService, Depends(get_note_service)]
