import json

from app.providers.cache.base import CacheProvider


class RedisCacheProvider(CacheProvider):
    """Redis-backed cache provider.

    Uses Redis for persistent, cross-process caching.
    Falls back gracefully if Redis is unavailable.
    """

    def __init__(self, redis_url: str):
        import redis.asyncio as aioredis

        self._client = aioredis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )

    async def get(self, key: str) -> str | None:
        try:
            return await self._client.get(key)
        except Exception:
            return None

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        try:
            if ttl_seconds:
                await self._client.setex(key, ttl_seconds, value)
            else:
                await self._client.set(key, value)
        except Exception:
            pass

    async def delete(self, key: str) -> None:
        try:
            await self._client.delete(key)
        except Exception:
            pass

    async def exists(self, key: str) -> bool:
        try:
            return await self._client.exists(key) > 0
        except Exception:
            return False

    async def close(self) -> None:
        try:
            await self._client.aclose()
        except Exception:
            pass
