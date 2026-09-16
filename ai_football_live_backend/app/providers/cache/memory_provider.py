import time

from app.providers.cache.base import CacheProvider


class InMemoryCacheProvider(CacheProvider):
    """V1 default: in-process dictionary cache.

    Zero infrastructure required.
    Data is lost on restart (acceptable for V1).
    """

    def __init__(self):
        self._store: dict[str, tuple[str, float | None]] = {}

    async def get(self, key: str) -> str | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at and time.time() > expires_at:
            del self._store[key]
            return None
        return value

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        expires_at = time.time() + ttl_seconds if ttl_seconds else None
        self._store[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return await self.get(key) is not None
