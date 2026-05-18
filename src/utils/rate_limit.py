from redis import Redis
import structlog
from src.config import settings
import time
from waygate import RedisBackend, WaygateEngine, make_engine

logger = structlog.get_logger()


class RateLimitEngineManager:
    def __init__(self):
        self._connected = False
        self._connection_time: float = 0
        self._msg: str = "Rate limit engine is not connected"

    def make_engine(self) -> WaygateEngine:
        try:
            redis = Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.retry_db,
            )
            start = time.perf_counter()
            redis.ping()
            self._connection_time = time.perf_counter() - start
            self._connected = True
            self._msg = "Rate limit engine connected"
            return WaygateEngine(
                backend=RedisBackend(url=settings.redis.retry_dsn.__str__())
            )
        except ConnectionError:
            self._msg = "Failed to connect to Redis due to connection error"
        except TimeoutError:
            self._msg = "Failed to connect to Redis due to timeout error"
        except Exception:
            self._msg = "Failed to connect to Redis"
        self._connected = False
        return make_engine()

    def log_connect(self):
        if not self._connected:
            logger.error(self._msg)
            logger.warning("Using in-memory rate limit engine")
            self._connected = True
            return
        logger.info(
            self._msg,
            connect_time=self._connection_time,
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.retry_db,
        )


rate_limit_engine = RateLimitEngineManager()
