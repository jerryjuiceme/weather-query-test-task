from src.repositories.cache import CacheRepositoryProtocol
from src.schemas import WeatherData

from .base import BaseCacheService
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.cache import CacheRepositoryProtocol


class WeatherCacheService(BaseCacheService[WeatherData]):
    read_schema = WeatherData

    def __init__(self, cache_repository: "CacheRepositoryProtocol") -> None:
        super().__init__(cache_repository)
