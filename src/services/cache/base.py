import json
from typing import Any, Generic, TypeVar, overload

from src.repositories.cache import CacheRepositoryProtocol
from pydantic import BaseModel

from .cache_key import CacheKey
from src.config import settings

ReadT = TypeVar("ReadT", bound=BaseModel)


class BaseCacheService(Generic[ReadT]):
    read_schema: type[ReadT]

    def __init__(self, cache_repository: CacheRepositoryProtocol) -> None:
        self.cache_repository = cache_repository
        self._key: CacheKey = CacheKey("null-key")

    ##########################
    ### Cache key methods ###
    ##########################
    # --------------- set key ----------------
    @overload
    def set_key(self, prefix: str) -> None: ...

    @overload
    def set_key(self, prefix: str, *args: Any) -> None: ...

    def set_key(self, prefix: str, *args: list[str]) -> None:
        self._key = CacheKey(prefix, *args)

    @property
    def key(self) -> str:
        return str(self._key)

    ###########################
    ### Basic cache methods ###
    ###########################

    async def get(self) -> ReadT | None:
        result = await self.cache_repository.get(str(self._key))
        if result is None:
            return None
        return self.read_schema.model_validate(json.loads(result))

    async def set(
        self, *, value: ReadT, expire: int | None = None, nx: bool = False
    ) -> bool:

        value_str = value.model_dump_json()

        return await self.cache_repository.set(
            str(self._key), value_str, expire=expire, nx=nx
        )

    async def delete(self) -> bool:
        return await self.cache_repository.delete(str(self._key))

    async def clear_pattern(self, pattern: str) -> int:
        pattern = settings.cache.prefix + ":" + pattern
        return await self.cache_repository.clear_pattern(pattern)
