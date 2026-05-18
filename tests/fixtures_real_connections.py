from typing import AsyncGenerator, Final
from redis import asyncio as aioredis
import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy_utils import create_database, database_exists, drop_database

from src.config import settings

TEST_CACHE_DB: Final[int] = 4

######################
### TEST DATABASE ###
######################


## Real database fixture and client ###
@pytest.fixture(scope="session")
async def tmp_database_real():
    assert settings.env == "TEST"

    db_url_sync = "postgresql+psycopg://%s:%s@%s:%s/%s" % (
        settings.db.username,
        settings.db.password,
        settings.db.host,
        settings.db.port,
        settings.db.database,
    )

    test_url = "postgresql+psycopg://%s:%s@%s:%s/postgres" % (
        settings.db.username,
        settings.db.password,
        settings.db.host,
        settings.db.port,
    )

    try:
        if not database_exists(test_url):
            pytest.exit("PostgreSQL server is not accessible", returncode=1)
    except Exception as e:
        pytest.skip(f"Cannot connect to PostgreSQL server: {e}")

    if not database_exists(db_url_sync):
        create_database(db_url_sync)
    yield

    if database_exists(db_url_sync):
        drop_database(db_url_sync)


@pytest.fixture(scope="session", name="engine")
async def engine_real(
    tmp_database_real,
) -> AsyncGenerator[AsyncEngine, None]:  # AsyncEngine:
    assert settings.env == "TEST"

    engine = create_async_engine(
        settings.db.DATABASE_URL_async,
        echo=False,
    )

    yield engine
    await engine.dispose()


######################
##### TEST CACHE #####
######################


### Real redis fixture ###
@pytest.fixture(scope="class", name="redis")
async def redis_real():
    """
    Real redis server fixture for tests
    TEST_CACHE_DB number 4 is reserved to all tests
    """
    # dsn = f"redis://{settings.redis.host}:{settings.redis.port}/{TEST_CACHE_DB}"
    # redis = await aioredis.from_url(
    #     dsn, encoding="utf-8", decode_responses=True, db=TEST_CACHE_DB
    # )
    redis = aioredis.Redis(
        decode_responses=True,
        encoding="utf-8",
        port=settings.redis.port,
        host=settings.redis.host,
        db=TEST_CACHE_DB,
    )
    try:
        if not await redis.ping():  # type: ignore
            pytest.exit("Redis server is not accessible", returncode=1)
    except Exception as e:
        pytest.skip(f"Cannot connect to Redis server: {e}")
    yield redis
    await redis.flushdb()
