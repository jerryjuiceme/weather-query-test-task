import structlog
from typing import Any
import redis.asyncio as redis
from src.config import settings

logger = structlog.get_logger()


class RedisCache:
    """
    Redis cache repository.
    """

    def __init__(self, redis: redis.Redis | None) -> None:
        self.redis_client = redis

    async def close(self):
        """
        Close the connection and the redis client.
        """
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    ###########################
    ### Basic cache methods ###
    ###########################

    async def get(self, key: str) -> Any | None:
        """
        Get a value from the cache.
        """
        if not self.redis_client:
            return None
        try:
            value = await self.redis_client.get(key)

            if value:
                logger.debug("Cache hit. Key: %s", key)
                return value

            logger.debug("Cache miss. Key: %s", key)
            return None

        except Exception as e:
            logger.error("Redis get error. Key: %s" % key, exc_info=e)
            return None

    async def set(
        self,
        key: str,
        value: str | int,
        expire: int | None = None,
        nx: bool = False,
    ) -> bool:
        """
        Set a key-value pair in the cache.

        Args:
            key (str): key name
            value (str): value to be stored
            expire (int | None, optional): set key expiration in seconds. Defaults to None.
            nx (bool, optional): if true, set key only if it does not exist. Defaults to False.
        """
        if not self.redis_client:
            return False
        try:
            expire = expire or settings.cache.ttl
            # serialized_value = json.dumps(value)
            serialized_value = value
            await self.redis_client.set(key, serialized_value, ex=expire, nx=nx)
            logger.debug("Redis set success. Key: %s" % key)
            return True
        except Exception as e:
            logger.error("Redis set error. Key: %s" % key, exc_info=e)
            return False

    async def incr(self, key: str, amount: int = 1) -> int:
        """
        Increment a value.
        """
        if not self.redis_client:
            return 0
        return await self.redis_client.incr(key, amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """
        Decrement a value.
        """
        if not self.redis_client:
            return 0
        return await self.redis_client.decr(key, amount)

    async def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.

        Args:
            key: cache key

        Returns:
            True if success, False otherwise
        """
        if not self.redis_client:
            return False
        try:
            await self.redis_client.delete(key)
            logger.debug("Cache key deleted. Key: %s", key)
            return True

        except Exception as e:
            logger.error("Redis delete error. Key: %s" % key, exc_info=e)
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Delete keys by pattern.

        Args:
            pattern: pattern for keys (for example, "notes:*")

        Returns:
            number of deleted keys
        """
        if not self.redis_client:
            return 0
        try:
            # hidden_pattern = settings.cache.prefix + ":" + pattern
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(
                    "Cache keys cleared. Pattern: %s, count: %s", (pattern, deleted)
                )
                return deleted
            return 0

        except Exception as e:
            logger.error(
                "Redis clear pattern error. Pattern: %s" % pattern,
                exc_info=e,
            )
            return 0

    ##############################
    ### Multiple cache methods ###
    ##############################

    async def set_many(
        self,
        cache_key: str,
        items: dict[str, str],
        expire: int | None = None,
    ) -> bool:
        if not self.redis_client:
            return False
        try:
            if not items:
                logger.debug("Redis set_many skipped. Empty items. Key: %s" % cache_key)
                return True

            await self.redis_client.hset(cache_key, mapping=items)  # type: ignore

            expire = expire or settings.cache.ttl
            await self.redis_client.expire(cache_key, expire)

            logger.debug(
                "Redis set_many success. Key: %s, count: %s" % (cache_key, len(items))
            )
            return True

        except Exception as e:
            logger.error("Redis set_many error. Key: %s" % cache_key, exc_info=e)
            return False

    async def get_many(self, cache_key: str) -> list[str] | None:
        if not self.redis_client:
            return None
        try:
            values = await self.redis_client.hgetall(cache_key)  # type: ignore

            if values:
                result = [
                    v.decode("utf-8") if isinstance(v, bytes) else v
                    for v in values.values()
                ]
                logger.debug("Cache hit. Key: %s, count: %s" % (cache_key, len(result)))
                return result

            logger.debug("Cache miss. Key: %s" % cache_key)
            return None

        except Exception as e:
            logger.error("Redis get_many error. Key: %s" % cache_key, exc_info=e)
            return None

    async def delete_many(self, cache_key: str) -> bool:
        if not self.redis_client:
            return False
        try:
            await self.redis_client.delete(cache_key)
            logger.debug("Cache key deleted. Key: %s" % cache_key)
            return True

        except Exception as e:
            logger.error("Redis delete_many error. Key: %s" % cache_key, exc_info=e)
            return False

    async def hset(
        self,
        cache_key: str,
        entity_key: str,
        entity_value: str,
        expire: int | None = None,
    ) -> bool:
        if not self.redis_client:
            return False
        try:
            await self.redis_client.hset(cache_key, entity_key, entity_value)  # type: ignore

            expire = expire or settings.cache.ttl
            await self.redis_client.expire(cache_key, expire)

            logger.debug(
                "Redis hset success. Key: %s, field: %s" % (cache_key, entity_key)
            )
            return True

        except Exception as e:
            logger.error(
                "Redis hset error. Key: %s, field: %s" % (cache_key, entity_key),
                exc_info=e,
            )
            return False

    async def hdelete(self, cache_key: str, entity_key: str) -> bool:
        if not self.redis_client:
            return False
        try:
            deleted = await self.redis_client.hdel(cache_key, entity_key)  # type: ignore

            if deleted > 0:
                logger.debug(
                    "Redis hdelete success. Key: %s, field: %s"
                    % (cache_key, entity_key)
                )
            else:
                logger.debug(
                    "Redis hdelete field not found. Key: %s, field: %s"
                    % (cache_key, entity_key)
                )

            return True

        except Exception as e:
            logger.error(
                "Redis hdelete error. Key: %s, field: %s" % (cache_key, entity_key),
                exc_info=e,
            )
            return False
