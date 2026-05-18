import json
import pytest  # noqa
from pydantic import BaseModel

from src.repositories.cache import CacheRepositoryProtocol


class CacheTestModel(BaseModel):
    """Test Pydantic model."""

    id: int
    name: str


class TestCache:
    """Test suite for InMemoryCache."""

    async def test_get_nonexistent_key(self, cache: CacheRepositoryProtocol):
        """Test getting a non-existent key returns None."""
        result = await cache.get("nonexistent")
        assert result is None

    async def test_set_and_get_string(self, cache: CacheRepositoryProtocol):
        """Test setting and getting a string value."""
        key = "test_key"
        value = "test_value"

        await cache.set(key, value, expire=2)
        result = await cache.get(key)

        assert result == value

    async def test_set_and_get_dict(self, cache: CacheRepositoryProtocol):
        """Test setting and getting a dict value."""
        key = "test_dict"
        value = {"name": "John", "age": 30}
        json_value = json.dumps(value)
        await cache.set(key, json_value, expire=2)
        result = await cache.get(key)
        assert result
        assert json.loads(result) == value

    async def test_set_and_get_pydantic_model(self, cache: CacheRepositoryProtocol):
        """Test setting and getting a Pydantic model."""
        key = "test_model"
        value = CacheTestModel(id=1, name="Test")

        await cache.set(key, value.model_dump_json(), expire=2)
        result = await cache.get(key)
        assert result
        assert json.loads(result) == {"id": 1, "name": "Test"}

    async def test_set_with_nx_new_key(self, cache: CacheRepositoryProtocol):
        """Test setting a new key with nx=True."""
        key = "new_key"
        value = "new_value"

        result = await cache.set(key, value, nx=True, expire=2)

        assert result is True
        assert await cache.get(key) == value

    async def test_set_with_nx_existing_key(self, cache: CacheRepositoryProtocol):
        """Test setting an existing key with nx=True does not overwrite."""
        key = "existing_key"
        original_value = "original"
        new_value = "new"

        await cache.set(key, original_value, expire=2)
        await cache.set(key, new_value, nx=True, expire=2)

        assert await cache.get(key) == original_value

    async def test_delete_existing_key(self, cache: CacheRepositoryProtocol):
        """Test deleting an existing key."""
        key = "to_delete"
        await cache.set(key, "value", expire=2)

        result = await cache.delete(key)

        assert result is True
        assert await cache.get(key) is None

    async def test_delete_nonexistent_key(self, cache: CacheRepositoryProtocol):
        """Test deleting a non-existent key returns True."""
        result = await cache.delete("nonexistent")
        assert result is True

    async def test_incr_new_key(self, cache: CacheRepositoryProtocol):
        """Test incrementing a new key starts from 0."""
        key = "counter"

        result = await cache.incr(key)

        assert int(result) == 1

    async def test_incr_existing_key(self, cache: CacheRepositoryProtocol):
        """Test incrementing an existing key."""
        key = "counter"
        await cache.set(key, 5, expire=2)

        result = await cache.incr(key)

        assert int(result) == 6

    async def test_incr_with_amount(self, cache: CacheRepositoryProtocol):
        """Test incrementing with custom amount."""
        key = "counter"
        await cache.set(key, 10, expire=2)

        result = await cache.incr(key, amount=5)

        assert result == 15

    async def test_decr_new_key(self, cache: CacheRepositoryProtocol):
        """Test decrementing a new key starts from 0."""
        key = "counter_new"

        result = await cache.decr(key)
        assert result
        assert int(result) == -1

    async def test_decr_existing_key(self, cache: CacheRepositoryProtocol):
        """Test decrementing an existing key."""
        key = "counter"
        await cache.set(key, 10, expire=2)

        result = await cache.decr(key)

        assert int(result) == 9

    async def test_decr_with_amount(self, cache: CacheRepositoryProtocol):
        """Test decrementing with custom amount."""
        key = "counter"
        await cache.set(key, 20, expire=2)

        result = await cache.decr(key, amount=7)

        assert result == 13

    async def test_clear_pattern_with_wildcard(self, cache: CacheRepositoryProtocol):
        """Test clearing keys by pattern with wildcard."""
        await cache.set("notes:1", "value1", expire=2)
        await cache.set("notes:2", "value2", expire=2)
        await cache.set("notes:3", "value3", expire=2)
        await cache.set("other:1", "other_value", expire=2)

        deleted = await cache.clear_pattern("notes:*")

        assert deleted == 3
        assert await cache.get("notes:1") is None
        assert await cache.get("notes:2") is None
        assert await cache.get("notes:3") is None
        assert await cache.get("other:1") == "other_value"

    async def test_clear_pattern_exact_match(self, cache: CacheRepositoryProtocol):
        """Test clearing keys by exact pattern."""
        await cache.set("exact_key", "value", expire=2)
        await cache.set("exact_key_2", "value2", expire=2)

        deleted = await cache.clear_pattern("exact_key")

        assert deleted == 1
        assert await cache.get("exact_key") is None
        assert await cache.get("exact_key_2") == "value2"

    async def test_clear_pattern_no_matches(self, cache: CacheRepositoryProtocol):
        """Test clearing with pattern that matches nothing."""
        await cache.set("key1", "value1", expire=2)

        deleted = await cache.clear_pattern("nonexistent:*")

        assert deleted == 0
        assert await cache.get("key1") == "value1"
