"""Redis caching service."""

import json
from typing import Any, Callable, Optional, TypeVar

import redis.asyncio as aioredis
from redis import Redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CacheService:
    """Redis-based caching service."""

    def __init__(self):
        self._client: Optional[Redis] = None
        self._async_client: Optional[aioredis.Redis] = None

    @property
    def client(self) -> Redis:
        if self._client is None:
            self._client = Redis.from_url(settings.redis_url, decode_responses=True)
        return self._client

    @property
    async def async_client(self) -> aioredis.Redis:
        if self._async_client is None:
            self._async_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        return self._async_client

    def get(self, key: str) -> Optional[str]:
        """Get a value from cache."""
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL."""
        try:
            ttl = ttl or settings.redis_cache_ttl
            return bool(self.client.setex(key, ttl, value))
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

    def get_json(self, key: str) -> Optional[Any]:
        """Get a JSON value from cache."""
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a JSON value in cache."""
        try:
            return self.set(key, json.dumps(value), ttl)
        except Exception as e:
            logger.error(f"Redis set_json error: {e}")
            return False

    def cached(self, key: str, ttl: Optional[int] = None):
        """Decorator to cache function results."""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            def wrapper(*args, **kwargs) -> T:
                cache_key = key.format(*args, **kwargs) if "{" in key else key
                cached_value = self.get_json(cache_key)
                if cached_value is not None:
                    return cached_value
                result = func(*args, **kwargs)
                self.set_json(cache_key, result, ttl)
                return result
            return wrapper
        return decorator

    def flush(self) -> bool:
        """Flush all cache."""
        try:
            return bool(self.client.flushdb())
        except Exception as e:
            logger.error(f"Redis flush error: {e}")
            return False


cache = CacheService()

