from typing import overload
from src.config import settings


class CacheKey:
    @overload
    def __init__(self, prefix: str) -> None: ...

    @overload
    def __init__(self, prefix: str, *args) -> None: ...

    def __init__(self, prefix: str, *args: list[str]) -> None:
        self.key: str = self.get_cache_key(prefix, *args)

    def get_cache_key(self, prefix: str, *args: list[str]) -> str:
        """
        Create a cache key.

        Args:
            prefix: prefix
            *args: other arguments

        Returns:
            returns ready  cache key
        """
        hidden_prefix = settings.cache.prefix + ":"
        parts = [prefix] + [str(arg) for arg in args]
        return hidden_prefix + ":".join(parts)

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return f"CacheKey({self.key})"  # self.key

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, other) -> bool:
        return self.key == other

    @staticmethod
    def pattern(prefix: str) -> str:
        """Function to create a pattern for cache search."""
        return f"{prefix}:*"
