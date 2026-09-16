from abc import ABC, abstractmethod


class CacheProvider(ABC):
    """Abstract interface for key-value caching."""

    @abstractmethod
    async def get(self, key: str) -> str | None:
        ...

    @abstractmethod
    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        ...
