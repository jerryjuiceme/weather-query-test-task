import json
import structlog
from typing import Any
from pydantic import BaseModel

logger = structlog.get_logger()


class InMemoryCache:
    """
    In-memory cache repository for testing purposes.
    """

    def __init__(self) -> None:
        self._storage: dict[str, Any] = {}

    async def close(self) -> None:
        pass

    async def get(self, key: str) -> Any | None:
        try:
            if key in self._storage:
                logger.debug("Cache hit", key=key)
                return self._storage[key]

            logger.debug("Cache miss", key=key)
            return None

        except Exception as e:
            logger.error("InMemory get error", key=key, exc_info=e)
            return None

    async def set(
        self,
        key: str,
        value: str | int,
        expire: int | None = None,
        nx: bool = False,
    ) -> bool:

        try:
            if nx and str(key) in self._storage:
                logger.debug("InMemory set skipped (nx=True, key exists)", key=key)
                return False

            if isinstance(value, BaseModel):
                serialized_value = value.model_dump_json()
            else:
                serialized_value = json.dumps(value)

            self._storage[str(key)] = json.loads(serialized_value)
            logger.debug("InMemory set success", key=key)
            return True

        except Exception as e:
            logger.error("InMemory set error", key=key, exc_info=e)
            return False

    async def incr(self, key: str, amount: int = 1) -> int:

        current = self._storage.get(str(key), 0)
        if not isinstance(current, int):
            current = 0

        new_value = current + amount
        self._storage[str(key)] = new_value
        return new_value

    async def decr(self, key: str, amount: int = 1) -> int:

        current = self._storage.get(str(key), 0)
        if not isinstance(current, int):
            current = 0

        new_value = current - amount
        self._storage[str(key)] = new_value
        return new_value

    async def delete(self, key: str) -> bool:

        try:
            if key in self._storage:
                del self._storage[str(key)]
                logger.debug("Cache key deleted", key=key)
            return True

        except Exception as e:
            logger.error("InMemory delete error", key=key, exc_info=e)
            return False

    async def clear_pattern(self, pattern: str) -> int:

        try:
            if pattern.endswith("*"):
                keys_to_delete = [
                    key
                    for key in self._storage.keys()
                    if key.startswith(pattern.replace("*", ""))
                ]
            else:
                keys_to_delete = [key for key in self._storage.keys() if key == pattern]

            deleted_count = len(keys_to_delete)
            for key in keys_to_delete:
                del self._storage[key]

            if deleted_count > 0:
                logger.info("Cache keys cleared.", pattern=pattern, count=deleted_count)

            return deleted_count

        except Exception as e:
            logger.error(
                "InMemory clear pattern error",
                pattern=pattern,
                exc_info=e,
            )
            return 0
