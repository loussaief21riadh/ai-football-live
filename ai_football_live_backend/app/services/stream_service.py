from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.stream.base import StreamProvider
from app.providers.stream.resolution import StreamResolution
from app.core.domain.match import StreamSource


class StreamService:
    """Orchestrates stream operations.

    Combines provider resolution with repository persistence.
    """

    def __init__(self, stream_provider: StreamProvider, db: AsyncSession):
        self._provider = stream_provider
        self._db = db

    async def resolve(self, match_id: int) -> StreamResolution:
        return await self._provider.resolve(match_id)

    async def list_streams(self, match_id: int) -> list[StreamSource]:
        return await self._provider.list_available(match_id)
