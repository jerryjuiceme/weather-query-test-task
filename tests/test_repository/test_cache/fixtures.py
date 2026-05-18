import pytest
from redis import asyncio as aioredis

from src.repositories.cache import CacheRepositoryProtocol
from src.repositories.cache.in_memory import InMemoryCache
from src.repositories.cache.redis import RedisCache


@pytest.fixture(scope="function")
def cache_in_memory():
    """Create a fresh cache instance for each test."""
    return InMemoryCache()


@pytest.fixture(scope="function")
async def redis_cache(redis: aioredis.Redis) -> CacheRepositoryProtocol:
    """Create a fresh cache instance for each test."""
    return RedisCache(redis)


@pytest.fixture(
    scope="function",
    name="cache",
    params=["redis_cache", "cache_in_memory"],
    ids=["Redis", "InMemory"],
)
def cache(request) -> CacheRepositoryProtocol:
    """Parametrized fixture that returns either Redis or InMemory cache."""
    return request.getfixturevalue(request.param)
