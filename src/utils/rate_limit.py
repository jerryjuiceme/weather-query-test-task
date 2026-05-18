from redis import asyncio as aioredis
from redis import Redis
import structlog
from src.config import settings
import time
from waygate import RedisBackend, WaygateEngine, make_engine

logger = structlog.get_logger()


class RateLimitEngineManager:
    def make_engine(self) -> WaygateEngine:
        try:
            redis = Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.retry_db,
            )
            start = time.perf_counter()
            redis.ping()
            logger.info(
                "Redis connection established",
                connect_time=time.perf_counter() - start,
            )
            return WaygateEngine(
                backend=RedisBackend(url=settings.redis.retry_dsn.__str__())
            )
        except ConnectionError:
            logger.error("Failed to connect to Redis due to connection error")
        except TimeoutError:
            logger.error("Failed to connect to Redis due to timeout error")
        except Exception:
            logger.error(
                "Failed to connect to Redis",
            )
        logger.warning("Using in-memory rate limit engine")
        return make_engine()


rate_limit_engine = RateLimitEngineManager()
