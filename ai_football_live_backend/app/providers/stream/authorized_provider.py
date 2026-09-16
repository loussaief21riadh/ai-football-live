from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.stream.base import StreamProvider
from app.providers.stream.resolution import StreamResolution
from app.database.models import StreamSourceModel
from app.core.enums.match_status import StreamAuthorizationStatus
from app.core.domain.match import StreamSource


class AuthorizedStreamProvider(StreamProvider):
    """Resolves streams from pre-registered authorized sources only.

    Does NOT discover, scrape, or proxy streams.
    Does NOT store or manage stream records.
    Only reads from the repository and returns authorized results.
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def resolve(self, match_id: int) -> StreamResolution:
        sources = await self._find_authorized(match_id)

        if not sources:
            return StreamResolution(
                available=False,
                stream=None,
                message="No authorized stream available for this match",
            )

        sources.sort(key=lambda s: self._quality_rank(s.quality), reverse=True)
        best = sources[0]

        return StreamResolution(
            available=True,
            stream=best,
            message="Stream available",
            alternatives=len(sources) - 1,
        )

    async def list_available(self, match_id: int) -> list[StreamSource]:
        return await self._find_authorized(match_id)

    async def _find_authorized(self, match_id: int) -> list[StreamSource]:
        query = (
            select(StreamSourceModel)
            .where(
                StreamSourceModel.match_id == match_id,
                StreamSourceModel.is_active == True,
                StreamSourceModel.authorization_status == StreamAuthorizationStatus.AUTHORIZED.value,
            )
        )
        result = await self._db.execute(query)
        models = list(result.scalars().all())
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: StreamSourceModel) -> StreamSource:
        return StreamSource(
            id=model.id,
            match_id=model.match_id,
            provider_name=model.provider_name,
            stream_url=model.stream_url,
            embed_url=model.embed_url,
            is_active=model.is_active,
            authorization_status=model.authorization_status,
            legal_basis=model.legal_basis,
            authorized_by=model.authorized_by,
            authorized_at=model.authorized_at,
            quality=model.quality,
            language=model.language,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _quality_rank(self, quality: str | None) -> int:
        ranks = {"4k": 4, "1080p": 3, "720p": 2, "480p": 1, "360p": 0}
        return ranks.get(quality or "", 0)
