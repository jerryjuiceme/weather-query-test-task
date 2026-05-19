from typing import AsyncGenerator, Generator
import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import AsyncRedisContainer
from src.config import settings

######################
### TEST DATABASE ###
######################


## TestContainer database fixture and client ###
@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Create a fresh database instance for each test."""
    with PostgresContainer(
        image="postgres:16",
        username="test",
        password="test",
        dbname="test_db",
    ) as postgres:
        yield postgres


@pytest.fixture(scope="session", name="engine")
async def engine(
    postgres_container,
) -> AsyncGenerator[AsyncEngine, None]:  # AsyncEngine:
    assert settings.env == "TEST"
    db_url = postgres_container.get_connection_url(driver="asyncpg")
    engine = create_async_engine(db_url, echo=False)

    yield engine
    await engine.dispose()


######################
##### TEST CACHE #####
######################


### TestContainer redis fixture ###
@pytest.fixture(scope="class", name="redis_container")
def redis_container():
    """
    Redis TestContainer fixture
    """
    # redis_img = "redis:alpine" # if valkey us not working use this
    valkey_img = "valkey/valkey:alpine"
    with AsyncRedisContainer(image=valkey_img) as redis_container:
        yield redis_container


@pytest.fixture(scope="function", name="redis")
async def redis_client(redis_container):
    redis = await redis_container.get_async_client(
        decode_responses=True,
        encoding="utf-8",
    )
    result = await redis.ping()  # type: ignore
    assert result
    yield redis
    await redis.flushdb()
