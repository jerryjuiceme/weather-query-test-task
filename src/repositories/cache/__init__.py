"""
Package containing the cache repository.


"""

__all__ = [
    "cache_manager",
    "CacheRepositoryProtocol",
    "CacheManager",
]

import structlog
import time
from typing import Any, Protocol

from .redis import RedisCache
from .in_memory import InMemoryCache
from src.config import settings
from redis import asyncio as aioredis
from redis.exceptions import ConnectionError, TimeoutError

logger = structlog.get_logger()


class CacheRepositoryProtocol(Protocol):
    """
    Cache repository protocol.
    """

    async def get(self, key: str) -> Any | None:
        """Get a value."""
        ...

    async def set(
        self,
        key: str,
        value: str | int,
        expire: int | None = None,
        nx: bool = False,
    ) -> bool:
        """Set a value."""
        ...

    async def delete(self, key: str) -> bool:
        """Delete a value."""
        ...

    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment a value."""
        ...

    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement a value."""
        ...

    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        ...

    async def close(self):
        """Close the connection and cache repository"""
        ...

    async def set_many(
        self,
        cache_key: str,
        items: dict[str, str],
        expire: int | None = None,
    ) -> bool: ...

    async def delete_many(self, cache_key: str) -> bool: ...

    async def get_many(self, cache_key: str) -> list[str] | None: ...

    async def hset(
        self,
        cache_key: str,
        entity_key: str,
        entity_value: str,
        expire: int | None = None,
    ) -> bool: ...

    async def hdelete(self, cache_key: str, entity_key: str) -> bool: ...


class CacheManager:
    """
    Cache manager.
    """

    def __init__(self):
        self._cache_repository: CacheRepositoryProtocol | None = None

    async def connect(self) -> None:
        if settings.env == "TEST":
            self._cache_repository = InMemoryCache()
        else:
            try:
                redis = await aioredis.from_url(
                    str(settings.redis.dsn),
                    encoding="utf-8",
                    decode_responses=True,
                )
                start = time.perf_counter()
                await redis.ping()  # type: ignore
                logger.info(
                    "Redis connection established. Connect time: %.6f seconds",
                    time.perf_counter() - start,
                )
            except ConnectionError:
                logger.error("Failed to connect to Redis due to connection error")
                redis = None
            except TimeoutError:
                logger.error("Failed to connect to Redis due to timeout error")
                redis = None
            except Exception as e:
                logger.error("Failed to connect to Redis", exc_info=e)
                redis = None
            self._cache_repository = RedisCache(redis)

    async def disconnect(self) -> None:
        if self._cache_repository:
            await self._cache_repository.close()
            self._cache_repository = None

        logger.info("Redis connection closed")

    async def get_cache_repository(self) -> CacheRepositoryProtocol:
        if self._cache_repository is None:
            await self.connect()
        return self._cache_repository  # type: ignore


cache_manager = CacheManager()


async def get_cache_repository() -> CacheRepositoryProtocol:
    return await cache_manager.get_cache_repository()
